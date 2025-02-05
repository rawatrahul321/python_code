# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import math


class CuttingNormalOrder(models.Model):
    _name = 'cutting.normal.order'
    _description = 'Cutting'

    @api.model
    def _get_default_uom(self):
        ProductUomObj = self.env['product.uom']
        UOMId = ProductUomObj.search([('name','in',('Piece','Unit(s)'))],limit=1)
        return UOMId and UOMId.id or False

    product_id = fields.Many2one('product.product',string='Product')
    size_id = fields.Many2one('size.size',string='Size',ondelete='restrict')
    size_qty = fields.Float(string='Qty')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    process_id = fields.Many2one('production.process',string='Production')
    product_uom_id = fields.Many2one('product.uom',string='Uom',default=_get_default_uom)
    color_id = fields.Many2one('color.color',string='Colour',ondelete='restrict')

class StitchingNormalOrder(models.Model):
    _name = 'stitching.normal.order'
    _description = 'Stitching'

    @api.model
    def _get_default_uom(self):
        ProductUomObj = self.env['product.uom']
        UOMId = ProductUomObj.search([('name','in',('Piece','Unit(s)'))],limit=1)
        return UOMId and UOMId.id or False

    product_id = fields.Many2one('product.product',string='Product')
    size_id = fields.Many2one('size.size',string='Size')
    size_qty = fields.Float(string='Qty')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    process_id = fields.Many2one('production.process',string='Production')
    product_uom_id = fields.Many2one('product.uom',string='Uom',default=_get_default_uom)
    color_id = fields.Many2one('color.color',string='Colour',ondelete='restrict')

class StitchingJobWork(models.Model):
    _name = 'stitching.job.work'
    _description = 'Job Work'

    jober_id = fields.Many2one('res.users',string='Jober')
    product_id = fields.Many2one('product.product',string='Jobwork')
    cost_per_piece = fields.Float(string='Cost Per Piece')
    total_cost = fields.Float(string='Total Cost')
    process_id = fields.Many2one('production.process',string='Production')

    @api.onchange('product_id','cost_per_piece','total_cost')
    def _onchange_product_id(self):
        if self.product_id and not self.total_cost and not self.cost_per_piece:
            self.cost_per_piece = self.product_id.standard_price or 0.0
        elif self.cost_per_piece and not self.total_cost:
            self.total_cost = self.cost_per_piece * self.process_id.total_produced_qty
        elif not self.cost_per_piece and self.total_cost and self.process_id.total_produced_qty:
            self.cost_per_piece = self.total_cost / self.process_id.total_produced_qty
