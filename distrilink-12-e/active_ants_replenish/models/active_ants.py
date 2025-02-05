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
from odoo.addons.active_ants_replenish.models.authorization import AuthorizeActiveAntsApiReplenish

logger = logging.getLogger(__name__)


class ActiveAntsConnection(models.Model):
    _inherit = 'active.ants.connection'
    _description = 'Active Ants Connection'

    def get_stock_mutation(self):
        conns = self.env['active.ants.connection'].search([])
        cron = self.env.ref('active_ants_replenish.ir_cron_sync_stock_mutation')
        purchase_order_obj = self.env['purchase.order']
        stock_mutations = []
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
                stock_mutation = AuthorizeActiveAntsApiReplenish(
                    conn.url, conn.user_name, conn.password).get_stock_mutation(api_token)
                self.env['audit.log'].put_audit_log(
                    cron.name, 'Success' if stock_mutation.get('messageCode') == 'OK' else 'Failed', stock_mutation, '')
                if stock_mutation.get('messageCode') != 'OK':
                    status = False
                    message = [stock_mutation.get('message')]
                result = stock_mutation.get('result')
                receive_more_qty = []
                receive_less_qty = []
                order_list = []
                stock_mutation_ids = []
                picking_list = []
                mutation_list = []
                ack_mutation = False
                if result:
                    for each in result:
                        logger.info('stock mutation.......%s'%(each))
                        if each.get('purchaseOrders'):
                            qty = each.get('purchaseOrders')[0].get('quantity')
                            purchase_order = purchase_order_obj.search(
                                [('name', '=', each.get('purchaseOrders')[0].get('purchaseOrderReference'))])
                            mutation_list.append(purchase_order.id)
                            dup_list = [x for x in mutation_list if mutation_list.count(x) > 1]
                            for picking in purchase_order.picking_ids:
                                if picking.state not in ['done', 'cancel']:
                                    for move in picking.move_ids_without_package:
                                        if each.get('sku') == move.product_id.default_code:
                                            if purchase_order.id in dup_list and move.quantity_done <= move.product_uom_qty:
                                                move.quantity_done += qty
                                            else:
                                                move.quantity_done = qty
                                    picking_list.append(picking.id)
                                    stock_mutation_ids.append(each.get('id'))
                                if picking.state == 'done' and each.get('id') not in stock_mutation_ids:
                                    stock_mutation_ids.append(each.get('id'))
                for pick in self.env['stock.picking'].browse(list(set(picking_list))):
                    try:
                        pick.button_validate()
                        is_more_qty = False
                        is_less_qty = False
                        for move in picking.move_ids_without_package:
                            if move.quantity_done > move.product_uom_qty:
                                is_more_qty = True
                            if move.quantity_done < move.product_uom_qty:
                                is_less_qty = True
                        if is_more_qty:
                            overprocessed_wizard = self.env['stock.overprocessed.transfer'].create({'picking_id': pick.id})
                            overprocessed_wizard.action_confirm()
                        if is_less_qty:
                            wizard = self.env['stock.backorder.confirmation'].create({'pick_ids': [(4, pick.id)]})
                            # wizard.process_cancel_backorder()
                            wizard.process()
                        order_list.append(purchase_order.id)
                        if pick.state == 'done':
                            ack_mutation = True
                    except Exception as e:
                        self.env['audit.log'].put_audit_log(cron.name, 'Failed', '', e)
                        logger.exception(str(e))

                for purchase in purchase_order_obj.browse(list(set(order_list))):
                    stock_mutations.append(purchase.name)
                    for line in purchase.order_line:
                        if line.qty_received > line.product_qty:
                            receive_more_qty_dict = {
                                'po': purchase.name,
                                'product':line.product_id.name,
                                'ordered_qty': line.product_qty,
                                'received_qty': line.qty_received,
                                'remaining_qty': line.product_qty - line.qty_received,
                            }
                            receive_more_qty.append(receive_more_qty_dict)
                        if line.qty_received < line.product_qty:
                            receive_less_qty_dict = {
                                'po': purchase.name,
                                'product': line.product_id.name,
                                'ordered_qty': line.product_qty,
                                'received_qty': line.qty_received,
                                'remaining_qty': line.product_qty - line.qty_received,
                            }
                            receive_less_qty.append(receive_less_qty_dict)
                logger.info('receive_more_qty..................%s'%(receive_more_qty))
                logger.info('receive_less_qty..................%s'%(receive_less_qty))
                if receive_more_qty or receive_less_qty:
                    template = self.env.ref('active_ants_replenish.email_template_purchase_order',False)
                    if template:
                        context = self.env.context
                        context['receive_more_qty'] = receive_more_qty
                        context['receive_less_qty'] = receive_less_qty
                        template.with_context(context).send_mail(conn.id, force_send=True)
                if stock_mutation_ids and ack_mutation:
                    ack_muation = AuthorizeActiveAntsApiReplenish(conn.url, conn.user_name, conn.password).ack_stock_mutations(
                        api_token, {'Ids': list(set(stock_mutation_ids))})
                    self.env['audit.log'].put_audit_log(
                        cron.name, 'Success' if ack_muation.get('messageCode') == 'OK' else 'Failed', ack_muation, '')
        if not message:
            message = ['%s Purchase Orders are updated with Stock Mutation' % (stock_mutations)]
        self.env['audit.log'].put_audit_log(cron.name, 'Success' if status == True else 'Failed', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def cancel_po_receipt(self):
        last20days = datetime.datetime.now() - datetime.timedelta(days=20)
        receipts = self.env['stock.picking'].search([
            ('backorder_id', '!=', False),
            ('create_date', '<=', last20days),
            ('state', 'not in', ['done', 'cancel']),
            ('picking_type_id.name', '=', 'Receipts')
        ])
        for receipt in receipts:
            receipt.action_cancel()
