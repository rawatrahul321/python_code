# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import math

class AccessoryProductTemplate(models.Model):
    _inherit = 'product.template'

    is_accessory = fields.Boolean(string='Is Accessory')

class AccessoryProductProduct(models.Model):
    _inherit = 'product.product'

    is_accessory = fields.Boolean(string='Is Accessory')

class AccessoryAccessory(models.Model):
    _name = 'accessory.accessory'
    _description = 'Accessory'

    product_id = fields.Many2one('product.product',string='Product')
    price_per_unit = fields.Float(string='Price Per Unit')
    quantity = fields.Float(string='Quantity',default=1.0)
    total_accessory_cost = fields.Float(compute='_total_cost_for_accessory', string="Total", store=True)
    process_id = fields.Many2one('production.process',string='Process')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_per_unit = self.product_id.standard_price or 0.0

    @api.depends('quantity','price_per_unit')
    def _total_cost_for_accessory(self):
        for accessory in self:
            accessory.total_accessory_cost = accessory.price_per_unit * accessory.quantity
            
class Size(models.Model):
    _name = 'size.size'
    _description = 'Size'

    name = fields.Char(string='Name',required=True)

class Color(models.Model):
    _name = 'color.color'
    _description = 'Color'

    name = fields.Char(string='Name',required=True)
