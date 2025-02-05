# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self and self.product_id and self.product_id.multi_uom_price_id:
            uom_ids = [i.uom_id.id for i in self.product_id.multi_uom_price_id]
            res.update({'domain': {'product_uom': [('id', 'in', uom_ids)]}})
            self.product_uom = False
        return res

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        res = super(SaleOrderLine, self).product_uom_change()
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self and self.product_uom:
            uom_price_id = self.env['product.multi.uom.price'].search([('pro_id', '=', self.product_id.id),
                                                                       ('uom_id', '=', self.product_uom.id)])
            self.price_unit = self.product_uom_qty * uom_price_id.price
