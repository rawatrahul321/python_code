# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import datetime

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    marketplace_id = fields.Char('MarketPlace Order ID')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', compute='_compute_sale_order', store=True)

    def _compute_sale_order(self):
        for rec in self:
            rec.sale_order_id = self.env['sale.order'].search([('name', '=', rec.origin)]).id

    @api.multi
    def getchannellogo(self):
        for rec in self:
            order = self.env['sale.order'].search([('name', '=', rec.origin)])
            return order

    @api.multi
    def getmarketplace(self):
        for rec in self:
            invoice = self.search([('number', '=', rec.origin)])
            creaditnote = self.env['sale.order'].search([('name', '=', invoice.origin)])
            return creaditnote

    def send_invoice_mail(self):
        template_id = self.env.ref('account.email_template_edi_invoice', False)
        ctx = dict(
            default_model='account.invoice',
            default_res_id=self.id,
            default_use_template=bool(template_id),
            default_template_id=template_id and template_id.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            force_email=True,
            active_ids= self.ids,
        )
        active_user = self.env['res.users'].browse(self._context.get('uid') or self._uid)
        if not active_user:
            active_user = self.env['res.users'].search([('use_as_current_user', '=', True)], limit=1)
        mail_compose = self.env['account.invoice.send'].with_context(ctx)
        mail_compose = mail_compose.create({'template_id': template_id.id})
        mail_compose.composer_id.template_id = template_id
        mail_compose.composer_id.onchange_template_id_wrapper()
        mail_compose.composer_id.email_from = active_user.partner_id.email or ''
        mail_compose.composer_id.author_id = active_user.partner_id.id or False
        mail_compose.send_and_print_action()

    def moveInvoiceToPaid(self, invoice, journal):
        register_payments_model = self.env['account.register.payments'].with_context(active_model='account.invoice')
        payment_method_manual_in = self.env.ref("account.account_payment_method_manual_in")
        ctx = {'active_model': 'account.invoice', 'active_ids': invoice.ids}
        register_payments = register_payments_model.with_context(ctx).create({
            'payment_date': datetime.datetime.now().date(),
            'journal_id': journal.id,
            'payment_method_id': payment_method_manual_in.id,
        })
        register_payments.create_payments()

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        res = super(AccountInvoice, self)._prepare_refund(invoice)
        if self.marketplace_id:
            res['marketplace_id'] = self.marketplace_id
        return res
