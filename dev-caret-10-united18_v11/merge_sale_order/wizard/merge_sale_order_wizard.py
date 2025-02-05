# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MergePurchaseOrder(models.TransientModel):
    _name = 'merge.sale.order'

    # merge_type = \
    #     fields.Selection([
    #         ('new_cancel',
    #             'Create new order and cancel all selected sale orders'),
    #         ('new_delete',
    #          'Create new order and delete all selected sale orders'),
    #         ('merge_cancel',
    #          'Merge order on existing selected order and cancel others'),
    #         ('merge_delete',
    #             'Merge order on existing selected order and delete others')],
    #         default='new_cancel')
    # sale_order_id = fields.Many2one('sale.order', 'Sale Order')

    @api.onchange('merge_type')
    def onchange_merge_type(self):
        res = {}
        for order in self:
            order.sale_order_id = False
            if order.merge_type in ['merge_cancel', 'merge_delete']:
                sale_orders = self.env['sale.order'].browse(
                    self._context.get('active_ids', []))
                res['domain'] = {
                    'sale_order_id':
                    [('id', 'in',
                        [sale.id for sale in sale_orders])]
                }
            return res

    @api.multi
    def merge_orders(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        print("sale_orders================",sale_orders)
        existing_so_line = False
        if len(self._context.get('active_ids', [])) < 2:
            raise UserError(
                _('Please select atleast two sale orders to perform '
                    'the Merge Operation.'))
        partner = sale_orders[0].partner_id.id
        if any(order.partner_id.id != partner for order in sale_orders):
            raise UserError(
                _('Please select Sale orders whose Customers are same to '
                    ' perform the Merge Operation.'))
        if any(order.state != 'sent' for order in sale_orders):
            raise UserError(
                _('Please select Sale orders which are in sent state '
                    ' perform the Merge Operation.'))
        mainSo = sale_orders[0]
        default = {'order_id': mainSo.id}
        for order in sale_orders:
            if order.id == mainSo.id:
                continue
            for line in order.order_line:
                if mainSo.order_line:
                    for soline in mainSo.order_line:
                        if line.product_id == soline.product_id and \
                                line.price_unit == soline.price_unit:
                            existing_so_line = soline
                            break
                if existing_so_line:
                    existing_so_line.product_uom_qty += \
                        line.product_uom_qty
                    so_taxes = [
                        tax.id for tax in existing_so_line.tax_id]
                    [so_taxes.append((tax.id))
                     for tax in line.tax_id]
                    existing_so_line.tax_id = \
                        [(6, 0, so_taxes)]
                else:
                    line.copy(default=default)
        for order in sale_orders:
            if order.id != mainSo.id:
                order.action_cancel()

