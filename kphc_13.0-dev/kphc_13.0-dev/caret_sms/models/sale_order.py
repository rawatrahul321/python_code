# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models, _


class SalesOrder(models.Model):
    _inherit = "sale.order"

    
    def action_confirm(self):
        res = super(SalesOrder, self).action_confirm()
        # Todo: fix issue but now add here send email module code
        template = self.env.ref('caret_sms.sale_order_email_template')
        if template:
            template.sudo().send_mail(self.id,force_send=True)
        sms_kphc_obj = self.env['kphc.sms']
        api_key = self.env['ir.config_parameter'].sudo().get_param('caret_sms.kphc_api_key')
        sale_sms_template = self.env.ref('caret_sms.sale_order_kphc_sms_template')
        sms_rendered_content = self.env['sms.body.template'].render_template(sale_sms_template.template_body, sale_sms_template.model, self.id)
        sender = self.env['ir.config_parameter'].sudo().get_param('caret_sms.sender')
        to_mobile = self.partner_id.phone
        to_number = to_mobile
        if to_mobile:
            if len(to_mobile) == 8:
                to_number = '965' + to_mobile
            elif '+' in to_mobile and len(to_mobile) == 12:
                to_number = to_mobile.replace('+','').strip()
            elif '+' in to_mobile and len(to_mobile) == 14:
                number = to_mobile.replace('+','').strip()
                to_number = number.replace(" ", "")
            else:
                to_number = to_mobile
            if len(to_number) == 11:
                if self.partner_id.lang == 'en_US':
                    lang = 1
                elif self.partner_id.lang == 'ar_001':
                    lang = 2
                else:
                    lang = 3
                for so in self:
                    message_vals = {'language':str(lang),
                                    'sender': sender,
                                    'to_number': to_number,
                                    'message':sms_rendered_content,
                                    'res_id':so.id or '',
                                    'res_model': sale_sms_template.model or '',
                                    'state':'draft'}
                    kphc_sms = sms_kphc_obj.create(message_vals)
                    kphc_sms.sendSMS()
        return res
