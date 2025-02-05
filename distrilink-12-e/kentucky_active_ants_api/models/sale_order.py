# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_active_kants_order = fields.Boolean('Is Kentucky Actvie Ants Order')
    state = fields.Selection(selection_add=[('kants_order', 'KAnts Order'),])
