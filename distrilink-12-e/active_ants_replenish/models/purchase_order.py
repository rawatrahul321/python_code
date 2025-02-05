# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging
import datetime
import sys,os

from odoo import api,models,fields
from odoo.addons.active_ants_api.models.authorization import AuthorizeActiveAntsApi
from odoo.addons.active_ants_replenish.models.authorization import AuthorizeActiveAntsApiReplenish

logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit='purchase.order'

    def date_by_adding_business_days(self,from_date, add_days):
        business_days_to_add = add_days
        current_date = from_date
        while business_days_to_add > 0:
            current_date += datetime.timedelta(days=1)
            weekday = current_date.weekday()
            if weekday >= 5:  # sunday = 6
                continue
            business_days_to_add -= 1
        date_time = current_date.strftime("%Y-%m-%d, %H:%M:%S")
        return date_time

    def button_confirm(self):
        expected_date = self.date_by_adding_business_days(self.date_order,3)
        conns = self.env['active.ants.connection'].search([])
        message = ''
        aa_warehouse = self.env['stock.warehouse'].search([('code', '=', 'AAVWH')])
        if aa_warehouse.id == self.picking_type_id.warehouse_id.id:
            for conn in conns:
                api_token_data = AuthorizeActiveAntsApi(conn.url, conn.user_name, conn.password).getApiToken().json()
                api_token = api_token_data.get('access_token')
                purchase_orderlines = []
                for line in self.order_line:
                    purchase_orderlines.append({
                        'Sku': line.product_id.default_code,
                        'Quantity': int(line.product_uom_qty),
                        'ExpectedDate': expected_date,
                    })
                data = {
                        'Reference':self.name,
                        'PurchaseOrderItems':purchase_orderlines,
                        'Comment': self.partner_ref or "",
                        'ExpectedDate': expected_date,
                }
                ants_purchase_order = AuthorizeActiveAntsApiReplenish(conn.url, conn.user_name, conn.password).post_purchase_orders(
                    api_token, data)
                self.env['audit.log'].put_audit_log('Import PO from Odoo to Active Ants',
                    'Success' if ants_purchase_order.get('messageCode') == 'OK' else 'Failed', ants_purchase_order, '')
                logger.info('ants_purchase_order.......%s'%(ants_purchase_order))
                message = ants_purchase_order.get('message')
                if ants_purchase_order.get('messageCode') == 'OK':
                    super(PurchaseOrder, self).button_confirm()
                if message:
                    self.message_post(body=message)
                    return self.env['wk.wizard.message'].genrated_message(
                        message, 'Active Ants Purchase Order: %s'%ants_purchase_order.get('messageCode'))
                else:
                    return True
        else:
            return super(PurchaseOrder, self).button_confirm()
