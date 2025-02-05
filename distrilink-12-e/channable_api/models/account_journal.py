# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import api, fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_pay_channable_invoice = fields.Boolean('Use For Channable Invoice Pay')
