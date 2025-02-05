# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPickingReturn(models.Model):
    # _name = 'stock.picking.return'
    _inherit = 'stock.picking'

    # purchase_id = fields.Many2one('return.order', related='move_lines.purchase_line_id.order_id',
    #                               string="Return Orders", readonly=True)
    return_id = fields.Many2one('return.order',

                               )
    @api.model
    def create(self, values):
        for rec in self:
            res = self.env['return.order'].search([('name', '=', self.origin)],limit=1)
            if res:
                rec.return_id = res
        return super(StockPickingReturn, self).create(values)


class StockMove(models.Model):
    _inherit = 'stock.move'

    # purchase_line_id = fields.Many2one('return.order.line', 'Return Order Line',
    #                                    ondelete='set null', index=True, readonly=True)
    return_line_id = fields.Many2one('return.order.line', 'Return Order Line',
                                       ondelete='set null', index=True, readonly=True)










