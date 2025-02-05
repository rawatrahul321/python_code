# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import math

class WashingProductionLine(models.Model):
    _name = 'washing.production.line'

    product_id = fields.Many2one('product.product',string='Product')
    uom_id = fields.Many2one('product.uom',string='Process UOM')
    location_id = fields.Many2one('stock.location',string='Stock Location')
    process_qty = fields.Float(string='Qty From Stitching')
    actual_received_qty = fields.Float(string='Actual Received Qty')
    missing_qty_from_stitch = fields.Float(string='Missing',store=True)
    washing_order_id = fields.Many2one('production.process',string='Washing Order')
    color_id = fields.Many2one('color.color',string='Colour',ondelete='restrict')
    size_id = fields.Many2one('size.size',string='Size')

    @api.onchange('product_id')
    def _onchange_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id and self.product_id.uom_id.id or False

    @api.multi
    @api.depends('process_qty','actual_received_qty')
    def _final_accessory_cost(self):
        for washing in self.washing_ids:
            washing.missing_qty_from_stitch = washing.process_qty - washing.actual_received_qty

class WashingProducedLine(models.Model):
    _name = 'washing.produced.line'

    product_id = fields.Many2one('product.product',string='Product')
    uom_id = fields.Many2one('product.uom',string='Process UOM')
    colour_id = fields.Many2one('color.color',string='Colour',ondelete='restrict')
    size_id = fields.Many2one('size.size',string='Size')
    colour_qty = fields.Float(string='Quantity')
    colour_washing_id = fields.Many2one('production.process',string='Washing Order')

    @api.onchange('product_id')
    def _onchange_uom_id(self):
        if self.product_id:
            print ("self.product_id.attribute_value_ids**************",self.product_id.attribute_value_ids)
            SizeAttrib = self.product_id.attribute_value_ids or False
            SizeVal = self.env['size.size'].search([('name','=',SizeAttrib.name)],limit=1)
            self.size_id = SizeVal and SizeVal.id or False
            self.uom_id = self.product_id.uom_id and self.product_id.uom_id.id or False