# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging

from odoo import _, api, fields, models, tools

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    "Templates for sending email with Bcc"

    _inherit = "mail.template"

    email_bcc = fields.Char('Bcc', help="Blind carbon copy recipients (placeholders may be used here)")

    @api.multi
    def generate_email(self, res_ids, fields=None):
        """Add email_bcc in list of fields for generate_email.

        Generates an email from the template for given the given model based on
        records given by res_ids.

        :param res_id: id of the record to use for rendering the template (model
                       is taken from template definition)
        :returns: a dict containing all relevant fields for creating a new
                  mail.mail entry, with one extra key ``attachments``, in the
                  format [(report_name, data)] where data is base64 encoded.
        """
        self.ensure_one()
        if fields is None:
            fields = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'email_bcc', 'reply_to', 'scheduled_date']
        elif fields and 'email_bcc' not in fields:
            fields.append('email_bcc')

        results = super(MailTemplate, self).generate_email(res_ids, fields)

        return results

    @api.multi
    def generate_recipients(self, results, res_ids):
        """Generates the recipients of the template. Default values can be generated
        instead of the template values if requested by template or context.
        Emails (email_to, email_cc) can be transformed into partners if requested
        in the context. """
        self.ensure_one()
        results = super(MailTemplate, self).generate_recipients(results, res_ids)

        records_company = None
        if self._context.get('tpl_partners_only') and self.model and results and 'company_id' in self.env[self.model]._fields:
            records = self.env[self.model].browse(results.keys()).read(['company_id'])
            records_company = {rec['id']: (rec['company_id'][0] if rec['company_id'] else None) for rec in records}

        for res_id, values in results.items():
            partner_ids = values.get('partner_ids', list())
            if self._context.get('tpl_partners_only'):
                mails = tools.email_split(values.pop('email_bcc', ''))
                Partner = self.env['res.partner']
                if records_company:
                    Partner = Partner.with_context(default_company_id=records_company[res_id])
                for mail in mails:
                    partner_id = Partner.find_or_create(mail)
                    partner_ids.append(partner_id)
            results[res_id]['partner_ids'] = partner_ids
        return results
