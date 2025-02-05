#  -*- coding: utf-8 -*-
 
from odoo import api, fields, models
 
class AccountAccount(models.Model):
    _inherit = "account.account"


    @api.multi
    @api.depends('name', 'code', 'company_id')
    def name_get(self):
        result = super(AccountAccount, self).name_get()
        result = []
        for account in self:
            name = '['+str(account.company_id.name)+']'+' ' + account.code + ' ' + account.name
            result.append((account.id, name))
        return result

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    picking_id = fields.Char('Picking Id')
    

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    @api.multi
    @api.depends('name', 'currency_id', 'company_id', 'company_id.currency_id')
    def name_get(self):
        res = []
        for journal in self:
            currency = journal.currency_id or journal.company_id.currency_id
            name = "[%s] %s (%s)" % (journal.company_id.name ,journal.name, currency.name)
            res += [(journal.id, name)]
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=None):
        context = self._context or {}
        context_value = context.get('account_journal_id')
        if context_value:
            account_search = self.search([('company_id','=',self.env.user.company_id.id)])
            args += [('id', 'in', account_search.ids)]
        return super(AccountJournal, self).name_search(name, args, operator=operator, limit=limit)

# class AccountJournal(models.Model):
#     _inherit = "account.invoices"

# class ProductTemplate(models.Model):
#     _inherit = "product.template"

class accountPaymentInh(models.Model):
    _inherit = "account.payment"


    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if not self.invoice_ids:
            # Set default partner type for the payment type
            if self.payment_type == 'inbound':
                self.partner_type = 'customer'
            elif self.payment_type == 'outbound':
                self.partner_type = 'customer'
        # Set payment method domain
        res = self._onchange_journal()
        if not res.get('domain', {}):
            res['domain'] = {}
        jrnl_filters = self._compute_journal_domain_and_types()
        journal_types = jrnl_filters['journal_types']
        journal_types.update(['bank', 'cash'])
        res['domain']['journal_id'] = jrnl_filters['domain'] + [('type', 'in', list(journal_types))]
        return res

class accountGeneralLedger(models.AbstractModel):
    _inherit = "report.account.report_generalledger"

    @api.model
    def get_report_values(self, docids, data=None):
        res = super(accountGeneralLedger, self).get_report_values(docids, data=data)
        res.update ({
            'flag': self.env.context.get('flag')
        })
        return res
