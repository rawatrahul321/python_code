# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models


class Message(models.Model):
    """Add Cc Bcc in Messages model: system notification
    (replacing res.log notifications), comments (OpenChatter discussion) and
    incoming emails.
    """
    _inherit = 'mail.message'

    email_cc = fields.Char('Cc', help='Carbon Copy message recipients')
    email_bcc = fields.Char('Bcc', help='Blind Carbon Copy message recipients')
