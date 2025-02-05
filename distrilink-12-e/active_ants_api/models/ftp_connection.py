# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging

from odoo import api, fields, models, _
from odoo.addons.active_ants_api.models.authorization import AuthorizeActiveAntsApi

logger = logging.getLogger(__name__)

class ftpConnection(models.Model):
    _inherit = 'ftp.connection'

    def fbm_process_flow(self):
        """process order flow with FBA/FBB flag and update stock warehouse based on that"""
        orders = self.env['sale.order'].search([('state', '=', 'channable_order')])
        cron = self.env.ref('channable_api.ir_cron_export_orders')
        export_products = []
        fbm_orders = 0
        ants_orders = 0
        invMessage = ''
        for order in orders:
            for line in order.order_line:
                if (line.product_id.is_fba and
                    (line.order_id.channable_channel_id and 'Amazon' in line.order_id.channable_channel_id.name)):
                    wh_location = self.env['stock.location'].search([('name', '=', 'WH')])
                    stock_quant = self.env['stock.quant'].search([
                        ('product_id', '=', line.product_id.id),
                        ('location_id.usage', '=', 'internal'),
                        ('location_id.location_id', '!=', wh_location.id)
                    ], limit=1)
                    warehouse = False
                    if stock_quant:
                        warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', stock_quant.location_id.id)])
                    if warehouse:
                        order.warehouse_id = warehouse.id
                    else:
                        order.warehouse_id = self.env.ref('channable_api.amazon_eu_warehouse').id
                    order.is_fbm_order = True
                elif (line.product_id.is_fbb and
                    (line.order_id.channable_channel_id and 'Bol' in line.order_id.channable_channel_id.name)):
                    order.warehouse_id = self.env.ref('channable_api.bol_warehouse').id
                    order.is_fbm_order = True
                elif line.product_id.is_active_ants:
                    warehouse = self.env['stock.warehouse'].search([('code', '=', 'AAVWH')])
                    if not warehouse:
                        warehouse = self.env['stock.warehouse'].create({'code': 'AAVWH', 'name': 'Active Ants Fulfilment Warehouse'})
                    order.warehouse_id = warehouse.id
                    order.is_active_ants_order = True
                else:
                    export_products.append(line.product_id.id)
            if order.is_fbm_order:
                fbm_orders += 1
                order.action_confirm()
                for picking in order.picking_ids:
                    try:
                        res = picking.button_validate()
                    except Exception as e:
                        if picking.state != 'done':
                            order.write({'delivery_validate_error': e})
                            self.env['audit.log'].put_audit_log(cron.name + 'Delivery Validate Error', 'Failed', '', e)
                invoice_id = order.action_invoice_create()
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
            if order.is_active_ants_order:
                self.processActiveAntsOrder(order)
                ants_orders += 1
        self.exportOrders(export_products)
        message = ['%s Orders are FBM Orders and %s Orders are Ants Orders' % (fbm_orders, ants_orders)]
        self.env['audit.log'].put_audit_log(cron.name, 'Success', '', message[0])
        if invMessage:
            message.append(invMessage)
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def processActiveAntsOrder(self, order):
        conns = self.env['active.ants.connection'].search([])
        for conn in conns:
            api_token_data = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).getApiToken().json()
            api_token = api_token_data.get('access_token')
            if api_token:
                setting_data = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).getSettings(api_token)
                if setting_data.get('result'):
                    setting_res = setting_data.get('result')
                    orderlines = []
                    delivery_country_code = ''
                    invoice_country_code = ''
                    if order.partner_shipping_id and order.partner_shipping_id.country_id:
                        delivery_country_code = order.partner_shipping_id.country_id.code
                    if order.partner_invoice_id and order.partner_invoice_id.country_id:
                        invoice_country_code = order.partner_invoice_id.country_id.code
                    for line in order.order_line:
                        vat = 0.0
                        for tax in line.tax_id:
                            vat += tax.amount
                        orderlines.append({
                            'Sku': line.product_id.default_code,
                            'Quantity': int(line.product_uom_qty),
                            'Name': line.name,
                            'Price': line.price_unit,
                            'VAT': vat,
                        })
                    paymentMethods = 1
                    language_id = 1
                    order_type_id = 1
                    if setting_res.get('paymentMethods'):
                        paymentMethods = setting_res.get('paymentMethods')[0]['id']
                    if setting_res.get('languages'):
                        language_id = setting_res.get('languages')[0]['id']
                    if setting_res.get('orderTypes'):
                        order_type_id = setting_res.get('orderTypes')[0]['id']
                    shipping_street = order.partner_shipping_id.street if order.partner_shipping_id and order.partner_shipping_id.street else ''
                    if not shipping_street:
                        shipping_street = order.partner_shipping_id.street2 if order.partner_shipping_id and order.partner_shipping_id.street2 else ''
                    billing_street = order.partner_invoice_id.street if order.partner_invoice_id and order.partner_invoice_id.street else ''
                    if not billing_street:
                        billing_street = order.partner_invoice_id.street2 if order.partner_invoice_id and order.partner_invoice_id.street2 else ''
                    if order.partner_shipping_id and order.partner_shipping_id.house_number and shipping_street:
                        if order.partner_shipping_id.house_number in shipping_street:
                            shipping_street = shipping_street.replace(order.partner_shipping_id.house_number, '')
                    if order.partner_invoice_id and order.partner_invoice_id.house_number and billing_street:
                        if order.partner_invoice_id.house_number in billing_street:
                            billing_street = billing_street.replace(order.partner_invoice_id.house_number, '')
                    data = {
                        'ExternalOrderNumber': order.name,
                        'Email': order.partner_id.email or '',
                        'PhoneNumber': order.partner_id.phone or '',
                        'PaymentMethodId': paymentMethods,
                        'LanguageId': language_id,
                        'OrderTypeId': order_type_id,
                        'OrderItems': orderlines,
                        'DeliveryAddressFirstName': order.partner_shipping_id.first_name if order.partner_shipping_id and order.partner_shipping_id.first_name else '',
                        'DeliveryAddressLastName': order.partner_shipping_id.last_name if order.partner_shipping_id and order.partner_shipping_id.last_name else '',
                        'DeliveryAddressHouseNumber': order.partner_shipping_id.house_number if order.partner_shipping_id and order.partner_shipping_id.house_number else '',
                        'DeliveryAddressPostalCode': order.partner_shipping_id.zip if order.partner_shipping_id and order.partner_shipping_id.zip else '',
                        'DeliveryAddressHouseNumberAddition': order.partner_shipping_id.house_number_ext if order.partner_shipping_id and order.partner_shipping_id.house_number_ext else '',
                        'DeliveryAddressStreet': shipping_street or '',
                        'DeliveryAddressCityName': order.partner_shipping_id.city if order.partner_shipping_id and order.partner_shipping_id.city else '',
                        'DeliveryAddressCountryIso': delivery_country_code or '',
                        'DeliveryAddressExtraAddress': order.partner_shipping_id.street2 if order.partner_shipping_id and order.partner_shipping_id.street2 else '',
                        'DeliveryAddressExtraName': order.partner_shipping_id.ce_company_name if order.partner_shipping_id and order.partner_shipping_id.ce_company_name else '',
                        'BillingAddressFirstName': order.partner_invoice_id.first_name if order.partner_invoice_id and order.partner_invoice_id.first_name else '',
                        'BillingAddressLastName': order.partner_invoice_id.last_name if order.partner_invoice_id and order.partner_invoice_id.last_name else '',
                        'BillingAddressHouseNumber': order.partner_invoice_id.house_number if order.partner_invoice_id and order.partner_invoice_id.house_number else '',
                        'BillingAddressPostalCode': order.partner_invoice_id.zip if order.partner_invoice_id and order.partner_invoice_id.zip else '',
                        'BillingAddressStreet': billing_street or '',
                        'BillingAddressCityName': order.partner_invoice_id.city if order.partner_invoice_id and order.partner_invoice_id.city else '',
                        'BillingAddressCountryIso': invoice_country_code or '',
                        'BillingAddressExtraAddress': order.partner_invoice_id.street2 if order.partner_invoice_id and order.partner_shipping_id.street2 else '',
                        'ClientReference': order.partner_id.ref if order.partner_id and order.partner_id.ref else ''

                    }
                    ants_order = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).postOrders(api_token, data)
                    self.env['audit.log'].put_audit_log('Post Order to Ants',
                        'Success' if ants_order.get('messageCode') == 'OK' else 'Failed', ants_order, '')
                    if ants_order.get('messageCode') == 'OK' or '(%s) already exists'%order.name in ants_order.get('message'):
                        order.write({'state': 'ants_order'})
                    logger.info(_("Active Ants Orders..., %s" %(ants_order)))
