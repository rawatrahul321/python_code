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
                        if order.channelengine_order_type_id:
                            for type_id in setting_res.get('orderTypes'):
                                if order.channelengine_order_type_id.code == str(type_id.get('id')):
                                    order_type_id = type_id.get('id')
                        else:
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
