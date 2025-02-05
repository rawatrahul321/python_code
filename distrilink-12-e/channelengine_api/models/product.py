# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    marchant_product_no = fields.Char('Merchant Product No.')
