# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import api, fields, models

class ProductSet(models.Model):
    _inherit = 'product.set'

    category_id = fields.Many2one('product.category', sting='Category')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    attrubute_restrict_id = fields.Many2one('product.attribute', 'Restrict Attribute')
    attribute_ids = fields.Many2many('product.attribute', string='Attributes', compute='_computeAttributeIds', store=True)

    @api.depends('attribute_line_ids')
    def _computeAttributeIds(self):
        for res in self:
            ids = []
            for line in res.attribute_line_ids:
                ids.append(line.attribute_id.id)
            res.attribute_ids = ids
