# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models
from odoo.exceptions import UserError

class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    description = fields.Selection([
        ('PRODUCT_DEFECT', 'Defective Product'),
        ('PRODUCT_UNSATISFACTORY', 'Unsatisfactory Product'),
        ('WRONG_PRODUCT', 'Wrong Product'),
        ('TOO_MANY_PRODUCTS', 'Too Many Products'),
        ('REFUSED', 'Refused'),
        ('REFUSED_DAMAGED', 'Refused (Damaged)'),
        ('WRONG_ADDRESS', 'Wrong Address'),
        ('NOT_COLLECTED', 'Not Collected'),
        ('WRONG_SIZE', 'Wrong Size'),
        ('OTHER', 'Other')
    ], string='Reason', required=True, default='PRODUCT_DEFECT')

    def _get_refund(self, inv, mode):
        self.ensure_one()
        if inv.state in ['draft', 'cancel']:
            self.env['audit.log'].put_audit_log(
                'Get Refund', 'Failed', '', 'Cannot create credit note for the draft/cancelled invoice.')
            raise UserError(_('Cannot create credit note for the draft/cancelled invoice.'))
        if inv.reconciled and mode in ('cancel', 'modify'):
            self.env['audit.log'].put_audit_log('Get Refund', 'Failed', '',
                'Cannot create a credit note for the invoice which is already reconciled, invoice should be unreconciled first, then only you can add credit note for this invoice.')
            raise UserError(_(
                'Cannot create a credit note for the invoice which is already reconciled, invoice should be unreconciled first, then only you can add credit note for this invoice.'))

        date = self.date or False
        description = self.description
        return inv.refund(self.date_invoice, date, description, inv.journal_id.id)
