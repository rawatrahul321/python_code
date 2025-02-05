# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models, api, _

class ZalandoLogo(models.Model):
    _name = 'zalando.logo'
    _description = 'Zalando Logo'
    _rec_name = 'marketPlace_logo'

    marketPlace_logo = fields.Binary('Zalando Logo')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def getzalandologo(self):
        for rec in self:
            zlogo = self.env['zalando.logo'].search([], order="id desc", limit=1)
            return zlogo

    @api.multi
    def getdeliverydate(self):
        for rec in self:
            for pick in self.sale_order_id.picking_ids:
                return pick.date_done if pick.date_done else pick.scheduled_date

    def getzalandolang(self):
        zalando_lang = self.sale_order_id.channelengine_order_type_id.name
        lang = zalando_lang.replace('-', '_')
        return lang
