# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_kentucky_active_ants = fields.Boolean('KANTS')
