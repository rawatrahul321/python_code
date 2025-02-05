# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import math

class FinishingOrderLine(models.Model):
    _name = 'finishing.order.line'

    product_id = fields.Many2one('product.product',string='Product')
    uom_id = fields.Many2one('product.uom',string='UOM')
    location_id = fields.Many2one('stock.location',string='Stock Location')
    process_qty = fields.Float(string='Process Qty')
    actual_received = fields.Float(string='Actual Received Qty')
    finishing_order_id = fields.Many2one('production.process',string='Finishing Order')
    color_id = fields.Many2one('color.color',string='Colour',ondelete='restrict')
    size_id = fields.Many2one('size.size',string='Size',ondelete='restrict')
    lot_id = fields.Many2one('stock.production.lot',string='Production Lot')
    mrp = fields.Float(compute='_get_mrp', string="MRP", store=True)

    @api.multi
    @api.depends('finishing_order_id.mrp_per_unit')
    def _get_mrp(self):
        for order in self:
            order.mrp = order.finishing_order_id.mrp_per_unit or 0.0

    @api.onchange('product_id')
    def _onchange_uom_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id and self.product_id.uom_id.id or False

class FinishingProducedLine(models.Model):
    _name = 'finishing.produced.line'

    product_id = fields.Many2one('product.product',string='Product')
    uom_id = fields.Many2one('product.uom',string='Process UOM')
    colour_id = fields.Many2one('color.color',string='Colour',ondelete='restrict')
    size_id = fields.Many2one('size.size',string='Size',ondelete='restrict')
    colour_qty = fields.Float(string='Quantity')
    finishing_process_id = fields.Many2one('production.process',string='Finishing Order')
    lot_id = fields.Many2one('stock.production.lot',string='Production Lot')
    mrp = fields.Float(compute='_get_mrp', string="MRP", store=True)

    @api.multi
    @api.depends('finishing_process_id.mrp_per_unit')
    def _get_mrp(self):
        for order in self:
            order.mrp = order.finishing_process_id.mrp_per_unit or 0.0


    @api.onchange('product_id')
    def _onchange_uom_id(self):
        if self.product_id:
            SizeAttrib = self.product_id.attribute_value_ids or False
            SizeVal = self.env['size.size'].search([('name','=',SizeAttrib.name)],limit=1)
            self.size_id = SizeVal and SizeVal.id or False
            self.uom_id = self.product_id.uom_id and self.product_id.uom_id.id or False