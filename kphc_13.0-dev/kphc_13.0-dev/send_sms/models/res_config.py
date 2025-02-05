from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_key = fields.Char('API Key')
    sender = fields.Char('Sender')
    is_phone_code_enable = fields.Boolean(string="Are you managing country calling code with customer's mobile number ?",
                                           help="If not enabled then it will pick country calling code from the country selected in customer.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            api_key=ICPSudo.get_param(
                'send_sms.api_key',False),
            sender=ICPSudo.get_param(
                'send_sms.sender',False),
            is_phone_code_enable=ICPSudo.get_param(
                'send_sms.is_phone_code_enable',False),

        )
        return res

    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param(
            "send_sms.api_key", self.api_key)
        ICPSudo.set_param(
            "send_sms.sender", self.sender)
        ICPSudo.set_param(
            "send_sms.is_phone_code_enable", self.is_phone_code_enable)
