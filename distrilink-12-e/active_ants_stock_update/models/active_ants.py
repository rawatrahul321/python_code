# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging
import datetime

from odoo import models
from odoo.addons.active_ants_api.models.authorization import AuthorizeActiveAntsApi
from odoo.addons.active_ants_stock_update.models.authorization import AuthorizeActiveAntsApiStock
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class ActiveAntsConnection(models.Model):
    _inherit = 'active.ants.connection'

    def sync_product_stock(self):
        conns = self.env['active.ants.connection'].search([])
        cron = self.env.ref('active_ants_stock_update.ir_cron_active_ants_sync_product_stock')
        message = []
        products = []
        product_stock_count = 0
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
                product_stock = AuthorizeActiveAntsApiStock(conn.url, conn.user_name, conn.password).get_product_stock(api_token)
                logger.info('product_stock.............................%s'%(product_stock))
                self.env['audit.log'].put_audit_log(
                        cron.name, 'Success' if product_stock.get('messageCode') == 'OK' else 'Failed', product_stock, '')
                if product_stock.get('messageCode') != 'OK':
                    status = False
                if product_stock.get('result'):
                    for data in product_stock.get('result'):
                        # TO DO client don't want it for sometime
                        # is_open_po = False
                        # po_line = self.env['purchase.order.line'].search([
                        #     ('product_id.default_code', '=', data.get('sku')),
                        #     ('order_id.state', '=', 'purchase')
                        # ])
                        # if po_line:
                        #     for line in po_line:
                        #         if line.order_id.picking_ids and all([x.state not in ['done'] for x in line.order_id.picking_ids]):
                        #             is_open_po = True
                        #             continue
                        # if not is_open_po:
                        product = self.env['product.product'].search([
                            ('default_code', '=', data.get('sku')), ('is_active_ants', '=', True)], order='id desc', limit=1)
                        if product:
                            location_id = self.env['stock.location'].search([('barcode', '=', 'AAVWH-STOCK')])
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
