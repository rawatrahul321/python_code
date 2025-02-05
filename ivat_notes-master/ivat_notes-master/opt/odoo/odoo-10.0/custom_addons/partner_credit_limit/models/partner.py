# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    over_credit = fields.Boolean('Allow Over Credit?', default=False)
    balance_credit = fields.Float('Balance Credit')
    
    @api.one
    @api.depends('credit')
    def get_partner_balance(self):
        print '*********--------*****',self.id
        print '** Credit Limit **',self.credit_limit,   self.credit
        self.balance_credit = self.credit_limit - self.credit