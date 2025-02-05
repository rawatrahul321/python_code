# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import api, models


class MailThread(models.AbstractModel):
    """Carry forward Cc and Bcc email from mail composer to mail.message and
    from mail.message to mail.mail for end to end value maintain.
    """
    _inherit = 'mail.thread'
    
    @api.multi
    def _notify_specific_email_values(self, message):
        """Add email_cc and email_bcc from message to mail.mail."""
        self.ensure_one()
        values = super(MailThread, self)._notify_specific_email_values(message)
        if hasattr(message, 'email_cc') and message.email_cc:
            values['email_cc'] = message.email_cc
        if hasattr(message, 'email_bcc') and message.email_bcc:
            values['email_bcc'] = message.email_bcc
        return values
