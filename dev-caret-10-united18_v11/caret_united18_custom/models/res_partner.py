# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons.bus.models.bus_presence import AWAY_TIMER
from odoo.addons.bus.models.bus_presence import DISCONNECTION_TIMER

class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit_custom = fields.Float('Credit Limit')

    @api.model
    def create(self,vals):
        print("partner vals===================",vals)
        ''' default Location and property set when create any company customer '''
        res = super(ResPartner,self).create(vals)
        company = self.env['res.company'].search([('partner_id', 'in', [res.id])])
        print("company======================",company)
        # if company.mobile:
        #     res.mobile = company.mobile
        AccountObj = self.env['account.account']
        Location = self.env['stock.location']
        fiscal_pos = False
        if res.state_id and\
           res.company_id.partner_id.state_id and\
           res.company_id.partner_id.state_id.id != res.state_id.id:
           fiscal_pos = self.env['account.fiscal.position'].\
                        search([('name', '=', 'Outer State GST'),
                                ('company_id.id', '=', res.company_id.id)])
        else:
            fiscal_pos = self.env['account.fiscal.position'].\
                        search([('name', '=', 'Inner State GST'),
                                ('company_id.id', '=', res.company_id.id)])
        res.sudo().property_account_position_id = fiscal_pos.id
        if res.company_id.parent_id.id:
            c_location_id = Location.sudo().search(['&',('company_id', '=', res.company_id.id),
                                             '&',('usage', '=', 'customer'),
                                             '&',('return_location' ,'=', False),
                                                 ('scrap_location' ,'=', False)],limit=1)
            v_location_id = Location.sudo().search(['&',('company_id', '=' ,res.company_id.id),
                                             '&',('usage', '=', 'supplier'),
                                             '&',('return_location' ,'=', False),
                                                 ('scrap_location' ,'=', False)],limit=1)

            account_receivable_id = AccountObj.sudo().search(['&',('company_id','=',res.company_id.id),
                                                           ('user_type_id.name','=','Receivable')],limit=1)
            account_payable_id = AccountObj.sudo().search(['&',('company_id','=',res.company_id.id),
                                                           ('user_type_id.name','=','Payable')],limit=1)
            res.sudo().property_stock_customer = c_location_id.id or res.property_stock_customer.id
            res.sudo().property_stock_supplier = v_location_id.id or res.property_stock_supplier.id
            res.sudo().property_account_receivable_id = account_receivable_id.id or res.property_account_receivable_id.id
            res.sudo().property_account_payable_id = account_payable_id.id or res.property_account_payable_id.id
        return res

    # @api.multi
    # def write(self,vals):
    #     if vals.get('mobile'):
    #         company = self.env['res.company'].search([('partner_id', 'in', [self.id])])
    #         company.mobile = vals['mobile']
    #     return super(ResPartner,self).write(vals)

    @api.multi
    @api.onchange('state_id','company_id')
    def _onchange_state_id(self):
        fiscal_pos = False
        if self.state_id and\
           self.company_id.partner_id.state_id and\
           self.company_id.partner_id.state_id.id != self.state_id.id:
           fiscal_pos = self.env['account.fiscal.position'].\
                        search([('name', '=', 'Outer State GST'),
                                ('company_id.id', '=', self.company_id.id)])
        else:
            fiscal_pos = self.env['account.fiscal.position'].\
                        search([('name', '=', 'Inner State GST'),
                                ('company_id.id', '=', self.company_id.id)])
        self.property_account_position_id = fiscal_pos

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=None):
        context = self._context or {}
        context_value = context.get('account_payment_partner')
        if context_value:
            if context_value == 'customer':
                customer_search = self.search([('company_id','=',self.env.user.company_id.id),
                                               ('customer','=',True)])
                args += [('id', 'in', customer_search.ids)]
            if context_value == 'supplier':
                customer_search = self.search([('company_id','=',self.env.user.company_id.parent_id.id),
                                               ('supplier','=',True)])
                args += [('id', 'in', customer_search.ids)]
        if context.get('return_partner_id'):
            customer_search = self.search([('company_id','=',self.env.user.company_id.parent_id.id),
                                               ('supplier','=',True)])
            args += [('id', 'in', customer_search.ids)]
        return super(ResPartner, self).name_search(name, args, operator=operator, limit=limit)

    @api.multi
    @api.depends('name', 'credit_limit_custom', 'credit')
    def name_get(self):
        context = self._context or {}
        context_value = context.get('sale_customer')
        result = []
        for record in self:
            if context_value:
                if record.credit_limit_custom:
                    name =  record.name + "/ Current Cr. " + "("+ str(record.credit_limit_custom - record.credit) + ")"
                else:
                    name = record.name
                result.append((record.id, name))
            else:
                result.append((record.id, record.name))
        return result


class ResCompany(models.Model):
    _inherit = 'res.company'

    credit_limit_custom = fields.Float(related='partner_id.credit_limit_custom', store=True)
    company_close = fields.Boolean('Company Closed', copy=False)
    dummy_state_id = fields.Many2one(
        'res.country.state', string='State', related='partner_id.state_id', store=True)
    dummy_mobile = fields.Char(related='partner_id.mobile', store=True)

    @api.multi
    def close_company(self):
        userIds = self.env['res.users'].search([('company_id', '=', self.id)])
        for user in userIds:
            user.active = False
        self.company_close = True

    # @api.multi
    # def write(vals):
    #     if vals.get('mobile'):
    #         self.partner_id.mobile = vals['mobile']
    #     return super(ResCompany, self).write(vals)

    # @api.model
    # def create(self,vals):
    #     res = super(ResCompany,self).create(vals)
    #     if vals.get('dummy_mobile'):
    #         res.sudo().partner_id = vals['dummy_mobile']
    #     return res
