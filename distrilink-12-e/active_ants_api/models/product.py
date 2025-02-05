# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_active_ants = fields.Boolean('ANTS')
    is_posted_to_aa = fields.Boolean('Is Posted to AA')
