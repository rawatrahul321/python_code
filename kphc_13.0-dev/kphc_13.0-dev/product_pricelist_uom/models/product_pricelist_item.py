# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductPriceListItemInherit(models.Model):
    _inherit = 'product.pricelist.item'

    applied_on = fields.Selection(selection_add=[
        ('product_uom', 'Product UOM'),
    ])

    product_uom = fields.Many2one('uom.uom', string="Product UOM")

    def _get_pricelist_item_name_price(self):
        res = super(ProductPriceListItemInherit, self)._get_pricelist_item_name_price()
        for rec in self:
            if rec.product_uom:
                rec.name = _("UOM: %s") % (rec.product_uom.name)
        return res
