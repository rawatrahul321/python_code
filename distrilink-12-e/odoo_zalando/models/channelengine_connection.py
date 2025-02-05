# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import datetime
import logging

from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

logger = logging.getLogger(__name__)

class ChannelEngineConnection(models.Model):
    _inherit = 'channelengine.connection'

    def processOrderTypeID(self, orderExtraData, channel, sale_order):
        countryCodeData = orderExtraData.get('ChannelOrderCountryCode')
        if channel.description in ['Zalando', 'zalando'] and orderExtraData and countryCodeData:
            countryCode = self.env['channelengine.country.code'].search([('name', '=', countryCodeData)])
            if not countryCode:
                countryCode = self.env['channelengine.country.code'].create({
                    'name', '=', countryCodeData
                })
                if countryCodeData == 'nl-BE':
                    countryCode.code = '2494'
                if countryCodeData == 'nl-NL':
                    countryCode.code = '2501'
                if countryCodeData == 'fr-BE':
                    countryCode.code = '2500'

            sale_order.channelengine_order_type_id = countryCode.id
            # lang = countryCodeData.replace('-', '_')
            # sale_order.lang = lang

    def processOrder(self, orderData):
        saleOrderObj = self.env['sale.order']
        channel = self.processChannel(
            orderData.get('ChannelName'), orderData.get('ChannelId'),
            orderData.get('GlobalChannelName'), orderData.get('ChannelOrderNo'))

        saleOrder = saleOrderObj.search([
            ('channable_channel_id', '=', channel.id)
        ])
        if not saleOrder:
            customer = self.processChannableCustomer(orderData)
            order_date = orderData.get('OrderDate').split('+')[0].split('.')[0]
            saleOrder = saleOrderObj.create({
                'channable_order_id': orderData.get('Id'),
                'partner_id': customer.get('resPartner').id,
                'channable_channel_id': channel.id,
                'channable_order_date': datetime.datetime.strptime(order_date, '%Y-%m-%dT%H:%M:%S').strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'partner_invoice_id': customer.get('billing_address').id,
                'partner_shipping_id': customer.get('shipping_address').id,
            })
            self.processSaleOrderLine(orderData.get('Lines'), saleOrder)
            self.processOrderTypeID(orderData.get('ExtraData'), channel, saleOrder)
        return saleOrder
