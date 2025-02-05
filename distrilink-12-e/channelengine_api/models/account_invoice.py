# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    marchant_return_no = fields.Char('Merchant Return No.')
    channel_return_no = fields.Char('Channel Return No.')
    return_reason = fields.Selection([
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
    ], string='Reason')
    customer_comment = fields.Char('Customer Comment')
    merchant_comment = fields.Char('merchant_comment')
    return_id = fields.Integer('Return ID')
    manual_returns = fields.Boolean('Manual Returns')

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        res = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice=date_invoice, date=date, description=description, journal_id=journal_id)
        if res.get('type') == 'out_refund':
            cr_nt = self.env['account.invoice'].search([('type', '=', 'out_refund')], order='id desc', limit=1)
            res['return_reason'] = description
            res['channel_return_no'] = invoice.marketplace_id
            res['marchant_return_no'] = invoice.marketplace_id
            res['manual_returns'] = True
            res['return_id'] = cr_nt.return_id + 1
        return res