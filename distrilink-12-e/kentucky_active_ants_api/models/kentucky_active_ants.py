# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging
import datetime
import re

from odoo import api, fields, models, _
from odoo.addons.active_ants_api.models.authorization import AuthorizeActiveAntsApi
from odoo.addons.active_ants_stock_update.models.authorization import AuthorizeActiveAntsApiStock
from odoo.addons.kentucky_active_ants_api.models.authorization import AuthorizeKentuckyActiveAntsApi
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class ActiveAntsConnection(models.Model):
    _name = 'kentucky.active.ants.connection'
    _description = 'Kentucky Active Ants Connection'

    name = fields.Char('Title')
    url = fields.Char('URL')
    user_name = fields.Char('User Name')
    password = fields.Char('Password')
    kants_order_type_id = fields.Char('Order Type ID', default='2515')

    def test_kentucky_active_ants_connection(self):
        api_token = AuthorizeActiveAntsApi(self.url, self.user_name, self.password).getApiToken()
        if not api_token.ok:
            raise UserError(_('Make sure Active Ants API details are correct.'))
        raise UserError(_('Connection Test Succeeded! Everything seems properly set up!'))

    def getTrackingCode(self, url):
        """We assume that biggest continuious digits are barcode from url."""
        allDigitGroup = re.findall(r'[0-9A-Z]+', url)
        return sorted(allDigitGroup, key=lambda x: len(x), reverse=True)[0] if allDigitGroup else None

    def get_kants_shipments(self):
        conns = self.env['kentucky.active.ants.connection'].search([])
        cron = self.env.ref('kentucky_active_ants_api.ir_cron_sync_kants_shipment_update')
        shipped_orders = []
        invMessage = ''
        message = []
        status = True
        for conn in conns:
            api_token_data = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).getApiToken().json()
            if api_token_data.get('error'):
                self.env['audit.log'].put_audit_log(
                        cron.name, 'Failed', api_token_data, '')
                message = [api_token_data.get('error_description')]
                status = False
            api_token = api_token_data.get('access_token')
            if api_token:
                shipments_data = AuthorizeKentuckyActiveAntsApi(
                    conn.url, conn.user_name, conn.password).post_shipment_byordertype(api_token, int(conn.kants_order_type_id))
                logger.info('shipments_data............................. %s'%(shipments_data))
                self.env['audit.log'].put_audit_log(
                    cron.name, 'Success' if shipments_data.get('messageCode') == 'OK' else 'Failed', shipments_data, '')
                if shipments_data.get('messageCode') != 'OK':
                    status = False
                    message = [shipments_data.get('message')]
                setting_data = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).getSettings(api_token)
                self.env['audit.log'].put_audit_log(
                    cron.name + 'Setting Data', 'Success' if setting_data.get('messageCode') == 'OK' else 'Failed', setting_data, '')
                transporter = ''
                tracking_code = ''
                tracking_url = ''
                shipment_ids = []
                if shipments_data.get('result'):
                    for shipment in shipments_data.get('result'):
                        order = self.env['sale.order'].search(
                            [('state', '=', 'kants_order'), ('name', '=', shipment.get('externalOrderNumber'))])
                        logger.info('order............................. %s'%(order))
                        if order:
                            setting = setting_data.get('result')
                            if setting and setting.get('shippingMethods'):
                                for method in setting.get('shippingMethods'):
                                    if method.get('id') == shipment.get('shippingMethodId'):
                                        transporter = method.get('name')
                                        break
                            logger.info('shipment.get(shippedColli)............................. %s'%(shipment.get('shippedColli')))
                            if shipment.get('shippedColli'):
                                for track in shipment.get('shippedColli'):
                                    tracking_code = conn.getTrackingCode(track.get('trackTraceUrl'))
                                    tracking_url = track.get('trackTraceUrl')
                            logger.info('Tracking Info................tracking_code: %s, tracking_url: %s, transporter: %s'%(
                                tracking_code, tracking_url, transporter))
                            if tracking_url and tracking_code and transporter:
                                order.action_confirm()
                                invoice_id = False
                                for picking in order.picking_ids:
                                    picking.write({
                                        'tracking_url': tracking_url,
                                        'tracking_code': tracking_code,
                                        'transporter': transporter,
                                        'is_delivery_not_validated': True
                                    })
                                    try:
                                        picking.button_validate()
                                        shipped_orders.append(order.name)
                                        picking.write({'is_delivery_not_validated': False})
                                        invoice_id = order.action_invoice_create()
                                        shipment_ids.append(shipment.get('id'))
                                    except Exception as e:
                                        if picking.state != 'done':
                                            order.write({'delivery_validate_error': e})
                                            self.env['audit.log'].put_audit_log(
                                                cron.name + 'Delivery Validate Error', 'Failed', '', e)
                                            logger.exception(str(e))
                                if invoice_id:
                                    invoice = self.env['account.invoice'].browse(invoice_id)
                                    invoice.action_invoice_open()
                                    invoice.sale_order_id = order.id
                                    invoice.send_invoice_mail()
                                    journal = self.env['account.journal'].search([('is_pay_channable_invoice', '=', True)], limit=1)
                                    if journal:
                                        if invoice.state == 'open':
                                            invoice.moveInvoiceToPaid(invoice, journal)
                                    else:
                                        invMessage = 'Invoice is not go to Paid state because journal are not Configured'
                                        self.env['audit.log'].put_audit_log(cron.name, 'Failed', '', invMessage)
                        else:
                            self.env['audit.log'].put_audit_log(cron.name, 'Failed', '', 'Please Fill Proper Tracking Details')
                            order.write({'delivery_validate_error': 'Please Fill Proper Tracking Details'})
                if shipment_ids:
                    ack_shipment = AuthorizeActiveAntsApi(
                        conn.url, conn.user_name, conn.password).ackShipmetsupdate(api_token, {'Ids': shipment_ids})
                    self.env['audit.log'].put_audit_log(
                        cron.name, 'Success' if ack_shipment.get('messageCode') == 'OK' else 'Failed', ack_shipment, '')
        if not message:
            message = ['%s Orders are updated shipment in ChannelEngine' % (shipped_orders)]
        self.env['audit.log'].put_audit_log(cron.name, 'Success' if status == True else 'Failed', '', message[0])
        if invMessage:
            message.append(invMessage)
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def sync_kants_product_stock(self):
        conns = self.env['kentucky.active.ants.connection'].search([])
        cron = self.env.ref('kentucky_active_ants_api.ir_cron_kentucky_active_ants_sync_product_stock')
        message = []
        products = []
        status = True
        product_stock_count = 0
        for conn in conns:
            api_token_data = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).getApiToken().json()
            if api_token_data.get('error'):
                self.env['audit.log'].put_audit_log(
                        cron.name, 'Failed', api_token_data, '')
                message = [api_token_data.get('error_description')]
                status = False
            api_token = api_token_data.get('access_token')
            if api_token:
                product_stock = AuthorizeActiveAntsApiStock(
                    conn.url, conn.user_name, conn.password).get_product_stock(api_token)
                self.env['audit.log'].put_audit_log(
                        cron.name, 'Success' if product_stock.get('messageCode') == 'OK' else 'Failed', product_stock, '')
                if product_stock.get('messageCode') != 'OK':
                    status = False
                logger.info('product_stock.............................%s'%(product_stock))
                if product_stock.get('result'):
                    for data in product_stock.get('result'):
                        # is_open_po = False
                        # po_line = self.env['purchase.order.line'].search([
                        #     ('product_id.default_code', '=', data.get('sku')),
                        #     ('product_id.is_kentucky_active_ants', '=', True),
                        #     ('order_id.state', '=', 'purchase')
                        # ])
                        # if not po_line:
                        #     po_line = self.env['purchase.order.line'].search([
                        #         ('product_id.default_code', '=', data.get('sku').upper()),
                        #         ('product_id.is_kentucky_active_ants', '=', True),
                        #         ('order_id.state', '=', 'purchase')
                        #     ])
                        # if po_line:
                        #     for line in po_line:
                        #         if line.order_id.picking_ids and all([x.state not in ['done'] for x in line.order_id.picking_ids]):
                        #             is_open_po = True
                        #             continue
                        # logger.info('is_open_po................%s'%(is_open_po))
                        # if not is_open_po:
                        product = self.env['product.product'].search([
                            ('default_code', '=', data.get('sku')), ('is_kentucky_active_ants', '=', True)], order='id desc', limit=1)
                        if not product:
                            product = self.env['product.product'].search([
                                ('default_code', '=', data.get('sku').upper()), ('is_kentucky_active_ants', '=', True)], order='id desc', limit=1)
                        if product:
                            location_id = self.env['stock.location'].search([('barcode', '=', 'WH-STOCK')])
                            inventory = self.env['stock.inventory'].search([
                                ('filter', '=', 'product'),
                                ('product_id', '=', product.id),
                                ('location_id', '=', location_id.id),
                                ('state', '=', 'confirm')
                            ])
                            if inventory:
                                inventory.action_validate()
                            if data.get('stock') < 0:
                                changeQty = self.env['stock.change.product.qty'].create({
                                    'product_id': product.id,
                                    'new_quantity': 0,
                                    'location_id': location_id.id or False
                                })
                            else:
                                changeQty = self.env['stock.change.product.qty'].create({
                                    'product_id': product.id,
                                    'new_quantity': data.get('stock'),
                                    'location_id': location_id.id or False
                                })
                            changeQty.change_product_qty()
                            product.write({'qty_available': data.get('stock')})
                            product_stock_count += 1
                            products.append(product.barcode)
                else:
                    message = [product_stock.get('message')]
        if not message and status:
            message = ['%s Products stock are Updated, Products list are %s' % (product_stock_count, products)]
        self.env['audit.log'].put_audit_log(cron.name, 'Success' if status == True else 'Failed', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
