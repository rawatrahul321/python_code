# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import api, models


class MailTemplate(models.Model):
    "Templates for sending email with Bcc"

    _inherit = 'mail.template'

    @api.multi
    def generate_recipients(self, results, res_ids):
        """Generates the recipients of the template. Default values can be generated
        instead of the template values if requested by template or context.
        Emails (email_to, email_cc) can be transformed into partners if requested
        in the context.
        """
        self.ensure_one()

        if self._context.get('enable_recipient_cc_bcc'):
            resultCc = dict()
            resultBcc = dict()
            # Super merges all email recipients into partner_ids. Can't extract
            # from partner_ids properly so we extract before and merge after
            # super.
            for res_id, values in results.items():
                resultCc[res_id] = values.pop('email_cc', '')
                resultBcc[res_id] = values.pop('email_bcc', '')

        results = super(MailTemplate, self).generate_recipients(results, res_ids)

        if self._context.get('enable_recipient_cc_bcc'):
            for res_id, values in results.items():
                results[res_id]['email_cc'] = resultCc.get(res_id, '')
                results[res_id]['email_bcc'] = resultBcc.get(res_id, '')

        return results
