# -*- coding: utf-8 -*-

from odoo import models, api


class ChangePasswordUser(models.TransientModel):
    """ A model to configure users in the change password wizard. """
    _inherit = 'change.password.user'
    _description = 'Change Password Wizard User'


    @api.multi
    def change_password_button(self):
        for line in self:
            if not line.new_passwd:
                raise UserError(_("Before clicking on 'Change Password', you have to write a new password."))
            line.user_id.write({'password': line.new_passwd})
            sms_template = self.env['ir.model.data'].get_object('caret_sms', 'user_password_change_sms_template')
            sms_rendered_content = self.env['sms.body.template'].render_template(sms_template.template_body, sms_template.model, self.id)
            api_key = self.env['ir.config_parameter'].sudo().get_param('caret_sms.textlocal_api_key')
            sender = self.env['ir.config_parameter'].sudo().get_param('caret_sms.sender')
            to_number = ''
            to_mobile = self.user_id.mobile or self.user_id.phone
            if to_mobile:
                if len(to_mobile) == 10:
                    to_number = str(91) + to_mobile
                elif '+' in to_mobile and len(to_mobile) == 13:
                    to_number = to_mobile.replace('+','').strip()
                elif '+' in to_mobile and len(to_mobile) == 11:
                    to_number = to_mobile.replace('+','').strip()
                elif '+' in to_mobile and len(to_mobile) == 11:
                    to_number = to_mobile.replace('+','').strip()
                else:
                    to_number = self.partner_id.mobile
                SMS_record = self.env['sms.sms'].create({'textlocal_api_key':api_key,
                                            'to_number': to_number,
                                            'message': sms_rendered_content,
                                            'sender': sender,
                                            'res_id': self.id or False,
                                            'res_model': 'change.password.user',
                                            })
                SMS_record.sendSMS()
        # don't keep temporary passwords in the database longer than necessary
        self.write({'new_passwd': False})
