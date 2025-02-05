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

    channelengine_order_type_id = fields.Many2one('channelengine.country.code',string='OrderTypeID')
    # lang = fields.Selection(selection='_get_languages', string='Language', validate=False)

    # @api.model
    # def _get_languages(self):
    #     langs = self.env['res.lang'].search([('translatable', '=', True)])
    #     return [(lang.code, lang.name) for lang in langs]
