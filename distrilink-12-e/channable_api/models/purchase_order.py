# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models, api
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        if res.partner_id:
            res.partner_ref = res.partner_id.ref
        return res

    @api.multi
    def write(self, values):
        if 'partner_id' in values:
            partner = self.env['res.partner'].browse(values.get('partner_id'))
            values['partner_ref'] = partner.ref
        return super(PurchaseOrder, self).write(values)
