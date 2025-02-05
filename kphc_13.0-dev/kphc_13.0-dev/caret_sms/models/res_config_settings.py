# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################


from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    kphc_api_key = fields.Char(string='API Key', help='KPHC API key you can get it from https://api-server14.com/api.key.aspx')
    sender = fields.Char(string='Sender Name', help='It must be name from your KPCH Sender')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            kphc_api_key=ICPSudo.get_param('caret_sms.kphc_api_key', default=False),
            sender= ICPSudo.get_param('caret_sms.sender', default='KPHC'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("caret_sms.kphc_api_key", self.kphc_api_key)
        ICPSudo.set_param("caret_sms.sender", self.sender)
