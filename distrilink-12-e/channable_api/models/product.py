# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import itertools

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    channable_product_id = fields.Char('Channable Product ID')
    channable_brand = fields.Char('Brand')
    channable_product_price = fields.Many2many('channable.product.price', string="Product Price")
    channable_vendor_ids = fields.Many2one('product.supplierinfo', string="Channable Vendors")
    is_review_product = fields.Boolean('Is Review Product')
    is_fba = fields.Boolean('FBA')
    is_fbb = fields.Boolean('FBB')
    # parent_reference = fields.Char('Parent Reference')

    def action_accept(self):
        product_id = self.product_variant_id.id
        lines = self.env['sale.order.line'].search([('product_id', '=', product_id)])
        order_ids = list(set([line.order_id.id for line in lines if line.order_id.is_channable_error_order]))
        for order in self.env['sale.order'].browse(order_ids):
            order.is_channable_error_order = False
        self.is_review_product = False

class ChannableProductPrice(models.Model):
    _name = 'channable.product.price'
    _description = 'Channable Product Price'

    name = fields.Char('Name of Website')
    channable_price_amount = fields.Float('Price')
    product_id = fields.Many2one('product.product', string="Product")

class Product(models.Model):
    _inherit = 'product.product'

    def action_accept(self):
        return self.product_tmpl_id.with_context({'default_product_id': self.id}).action_accept()
