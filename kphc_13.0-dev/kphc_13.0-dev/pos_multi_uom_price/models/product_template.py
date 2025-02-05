# -*- coding: utf-8 -*-

from odoo import models, fields, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    multi_uom_price_id = fields.One2many('product.multi.uom.price', 'product_id', string=_("UOM price"))


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    multi_uom_price_id = fields.One2many('product.multi.uom.price', 'pro_id', string=_("UOM price product"))

