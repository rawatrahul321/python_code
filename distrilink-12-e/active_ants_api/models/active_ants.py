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
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class ActiveAntsConnection(models.Model):
    _name = 'active.ants.connection'
    _description = 'Active Ants Connection'

    name = fields.Char('Title')
    url = fields.Char('URL')
    user_name = fields.Char('User Name')
    password = fields.Char('Password')

    def test_active_ants_connection(self):
        api_token = AuthorizeActiveAntsApi(self.url, self.user_name, self.password).getApiToken()
        if not api_token.ok:
            raise UserError(_('Make sure Active Ants API details are correct.'))
        raise UserError(_('Connection Test Succeeded! Everything seems properly set up!'))

    def getTrackingCode(self, url):
        """We assume that biggest continuious digits are barcode from url."""
        allDigitGroup = re.findall(r'[0-9A-Z]+', url)
        return sorted(allDigitGroup, key=lambda x: len(x), reverse=True)[0] if allDigitGroup else None

    def get_ants_shipments(self):
        conns = self.env['active.ants.connection'].search([])
        cron = self.env.ref('active_ants_api.ir_cron_sync_ants_shipment_update')
        shipped_orders = 0
        shipped_orders_list = []
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
                shipments_data = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).getShipments(api_token)
                logger.info('shipments_data............................. %s'%(shipments_data))
                self.env['audit.log'].put_audit_log(
                    cron.name, 'Success' if shipments_data.get('messageCode') == 'OK' else 'Failed', shipments_data, '')
                if shipments_data.get('messageCode') != 'OK':
                    status = False
                    message = [shipments_data.get('message')]
                setting_data = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).getSettings(api_token)
                self.env['audit.log'].put_audit_log(
                    cron.name, 'Success' if setting_data.get('messageCode') == 'OK' else 'Failed', setting_data, '')
                transporter = ''
                tracking_code = ''
                tracking_url = ''
                shipment_ids = []
                if shipments_data.get('result'):
                    for shipment in shipments_data.get('result'):
                        order = self.env['sale.order'].search([('state', '=', 'ants_order'), ('name', '=', shipment.get('externalOrderNumber'))])
                        if order:
                            setting = setting_data.get('result')
                            if setting and setting.get('shippingMethods'):
                                for method in setting.get('shippingMethods'):
                                    if method.get('id') == shipment.get('shippingMethodId'):
                                        transporter = method.get('name')
                                        break
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
                                        shipped_orders += 1
                                        shipped_orders_list.append(order.name)
                                        picking.write({'is_delivery_not_validated': False})
                                        invoice_id = order.action_invoice_create()
                                        shipment_ids.append(shipment.get('id'))
                                    except Exception as e:
                                        if picking.state != 'done':
                                            order.write({'delivery_validate_error': e})
                                            self.env['audit.log'].put_audit_log(cron.name, 'Failed', '', str(e))
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
                            order.write({'delivery_validate_error': 'Please Fill Proper Tracking Details'})
                            self.env['audit.log'].put_audit_log(cron.name, 'Failed', '', 'Please Fill Proper Tracking Details')
                if shipment_ids:
                    ack = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).ackShipmetsupdate(api_token, {'Ids': shipment_ids})
                    self.env['audit.log'].put_audit_log(
                        cron.name, 'Success' if ack.get('messageCode') == 'OK' else 'Failed', ack, '')
        if not message:
            message = ['%s Orders are updated shipment in ChannelEngine' % (shipped_orders)]
            if invMessage:
                message.append(invMessage)
        self.env['audit.log'].put_audit_log(
            cron.name, 'Success' if status == True else 'Failed', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def add_product_to_ants(self):
        products = self.env['product.template'].search([('is_active_ants', '=', True), ('is_posted_to_aa', '=', False)])
        conns = self.env['active.ants.connection'].search([])
        cron = self.env.ref('active_ants_api.ir_cron_post_products_to_ants')
        done_products = []
        message = []
        status = True
        for conn in conns:
            auth = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password)
            api_token_data = auth.getApiToken().json()
            if api_token_data.get('error'):
                self.env['audit.log'].put_audit_log(cron.name, 'Failed', api_token_data, '')
                message = [api_token_data.get('error_description')]
                status = False
            api_token = api_token_data.get('access_token')
            if api_token:
                for product in products:
                    ants_product = auth.getProducts(api_token, product.default_code)
                    logger.info('ants_product................SKU: %s, Barcode: %s, Response: %s'%(
                        product.default_code, product.barcode, ants_product))
                    self.env['audit.log'].put_audit_log(
                        cron.name + 'Get Products', 'Success' if ants_product.get('messageCode') == 'OK' else 'Failed', ants_product, '')
                    if ants_product.get('result') and ants_product.get('result').get('sku') == product.default_code:
                        product.is_posted_to_aa = True
                    else:
                        product_data = {
                            'Name': product.name,
                            'Sku': product.default_code,
                            'Barcode': product.barcode,
                            'Description': product.description,
                            'CostPrice': product.standard_price,
                            'PriceA': product.list_price
                        }
                        stock_qty = self.env['stock.warehouse.orderpoint'].search(
                            [('product_id', '=', product.id)], order='id desc', limit=1)
                        if stock_qty:
                            product_data.update({
                                'StockMinimum': int(stock_qty.product_min_qty),
                                'StockMaximum': int(stock_qty.product_max_qty)
                            })
                        post_result = auth.postProducts(api_token, product_data)
                        logger.info('post_result................%s'%(post_result))
                        self.env['audit.log'].put_audit_log(
                            cron.name, 'Success' if post_result.get('messageCode') == 'OK' else 'Failed', post_result, '')
                        if post_result.get('messageCode') != 'OK':
                            status = False
                            message = [post_result.get('message')]
                        if post_result.get('messageCode') == 'OK':
                            done_products.append(product.default_code)
                            product.is_posted_to_aa = True
        if not message:
            message = ['%s Products are Posted in Active Ants' % (done_products)]
        self.env['audit.log'].put_audit_log(cron.name, 'Success' if status == True else 'Failed', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def edit_product_to_ants(self):
        last30Min = datetime.datetime.now() - datetime.timedelta(minutes=30)
        cron = self.env.ref('active_ants_api.ir_cron_post_products_edit_to_ants')
        products = self.env['product.template'].search([('is_active_ants', '=', True), ('write_date', '>=', last30Min)])
        conns = self.env['active.ants.connection'].search([])
        edit_products = []
        message = []
        status = True
        for conn in conns:
            api_token_data = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).getApiToken().json()
            if api_token_data.get('error'):
                self.env['audit.log'].put_audit_log(cron.name, 'Failed', api_token_data, '')
                message = [api_token_data.get('error_description')]
                status = False
            api_token = api_token_data.get('access_token')
            if api_token:
                for product in products:
                    product_data = {
                        'Name': product.name,
                        'Sku': product.default_code,
                        'Description': product.description,
                        'CostPrice': product.standard_price,
                        'PriceA': product.list_price
                    }
                    stock_qty = self.env['stock.warehouse.orderpoint'].search([
                        ('product_id', '=', product.id), ('write_date', '>=', last30Min)], order='id desc', limit=1)
                    if stock_qty:
                        product_data.update({
                            'StockMinimum': stock_qty.product_min_qty,
                            'StockMaximum': stock_qty.product_max_qty
                        })
                    edit_result = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).postProductEdit(api_token, product_data)
                    logger.info('edit_result................%s'%(edit_result))
                    self.env['audit.log'].put_audit_log(
                        cron.name, 'Success' if edit_result.get('messageCode') == 'OK' else 'Failed', edit_result, '')
                    if edit_result.get('messageCode') != 'OK':
                        status = False
                        message = [edit_result.get('message')]
                    if edit_result.get('messageCode') == 'OK':
                        edit_products.append(product.barcode)
        if not message:
            message = ['%s Products are Edited in Active Ants' % (edit_products)]
        self.env['audit.log'].put_audit_log(cron.name, 'Success' if status == True else 'Failed', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
