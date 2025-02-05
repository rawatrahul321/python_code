# -*- coding: utf-8 -*-

from odoo import tools,models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class SaleProductCategory(models.TransientModel):
    """sale order report filter by product category"""
    _name = 'sale.product.category.wizard'

    def _default_order_ids(self):
        order_ids = self._context.get('active_model') == 'sale.order' and self._context.get('active_ids') or []
        return order_ids

    order_ids = fields.Many2many('sale.order', string='Sale Orders', default=_default_order_ids)
    category_ids = fields.Many2many('product.category', string='Product Category',
                    domain=[('parent_id', '=', False)])
    sol_ids = fields.Many2many('sale.order.line', string='SO lines')

    @api.multi
    @api.onchange('order_ids', 'category_ids')
    def _onchange_category(self):
        sol_ids = []
        if self.category_ids:
            sol_ids = self.env['sale.order.line'].search([
                ('order_id', 'in', self.order_ids.ids),
                ('product_id.categ_id.id', 'child_of', self.category_ids.ids)]).ids
        else:
            sol_ids = self.env['sale.order.line'].search([
                ('order_id', 'in', self.order_ids.ids)]).ids
        self.sol_ids = sol_ids

    @api.multi
    def print_sale_order_report(self):
        return self.env.ref('caret_united18_custom.filter_sale_order_report').report_action([],
                                                                        data={'orders': self.order_ids.ids,
                                                                              'category': self.category_ids.ids,
                                                                              'order_lines': self.sol_ids.ids})
