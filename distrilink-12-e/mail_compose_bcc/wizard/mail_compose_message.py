# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models


class MailComposer(models.TransientModel):
    """ Inheriting 'Generic message composition wizard' for adding Cc and Bcc
    address feature.
    """
    _inherit = 'mail.compose.message'

    email_cc = fields.Char('Cc', help='Carbon Copy message recipients')
    email_bcc = fields.Char('Bcc', help='Blind Carbon Copy message recipients')

    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        self = self.with_context(enable_recipient_cc_bcc=True)
        if fields is None:
            fields = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'email_bcc', 'reply_to', 'attachment_ids', 'mail_server_id']
        else:
            if 'email_bcc' not in fields:
                fields.append('email_bcc')
        return super(MailComposer, self).generate_email_for_composer(template_id, res_ids, fields=fields)

    def get_mail_values(self, res_ids):
        """Add Cc and Bcc address according for generate the values that will
        be used by send_mail to create mail_messages or mail_mails.
        """
        self.ensure_one()
        results = super(MailComposer, self).get_mail_values(res_ids)
        for res_id in res_ids:
            results[res_id]['email_cc'] =  results[res_id].get('email_cc', '') + self.email_cc if self.email_cc else ''
            results[res_id]['email_bcc'] =  results[res_id].get('email_bcc', '') + self.email_bcc if self.email_bcc else ''
        return results
