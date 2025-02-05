# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    textlocal_api_key = fields.Char(string='API Key',help='Textlocal API key you can get it from https://control.textlocal.in/settings/apikeys/')
    sender = fields.Char(string='Sender Name',help='It must be name from your Textlocal Sender')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            textlocal_api_key=ICPSudo.get_param('caret_sms.textlocal_api_key', default=False),
            sender= ICPSudo.get_param('caret_sms.sender', default='UNITED'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("caret_sms.textlocal_api_key", self.textlocal_api_key)
        ICPSudo.set_param("caret_sms.sender", self.sender)
