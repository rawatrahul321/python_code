# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re

class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def create(self,vals):
        percent_check = re.findall("\d+", vals['name'])
        if 'Purchase' in vals['name']:
            vals.update({'type_tax_use' : 'purchase'})
        if 'Sale' in vals['name']:
            vals.update({'type_tax_use' : 'sale'})
        if vals.get('name') == 'GST '+str(percent_check[0])+'%':
            if 'purchase' == vals.get('type_tax_use'):
                vals.update({'name' : 'GST Purchase '+str(percent_check[0])+'%'})
            else:
                vals.update({'name' : 'GST Sale '+str(percent_check[0])+'%'})
        return super(AccountTax,self).create(vals)

class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    @api.model
    def create(self,vals):
        if 'Inter State' in vals['name']:
            vals.update({'name' : 'Inner State GST'})
        if 'Export' in vals['name']:
            vals.update({'name' : 'Outer State GST'})
        return super(AccountFiscalPosition,self).create(vals)

