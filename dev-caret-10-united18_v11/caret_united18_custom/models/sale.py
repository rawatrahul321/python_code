#  -*- coding: utf-8 -*-

import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
import datetime

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    so_reference = fields.Char()
    login_company_check = fields.Boolean(compute='_get_login_company')

    @api.multi
    @api.depends('company_id')
    def _get_login_company(self):
        if self.company_id.id == self.env.user.company_id.id:
            self.login_company_check = True
        else:
            self.login_company_check = False

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def _compute_tax_id(self):

        for line in self:
            taxes = self.env['account.tax']
            taxesRec = self.env['account.tax']
            sol = self.env['sale.order.line'].search([
                ('id', '=', int(line.order_line_ref or 0))])
            poTaxIds = []
            taxIds = False
            if sol:
                for tax in sol.tax_id:
                    taxIds = taxes.search([
                        ('description', '=', tax.description),
                        ('type_tax_use', '=', 'purchase'),
                        ('company_id', '=', line.order_id.company_id.id)])
                    taxesRec += taxIds
                    # poTaxIds.append(taxIds)
                print("taxesRec-----=============",taxesRec)
            else:
                taxesRec = line.product_id.supplier_taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            # taxes = line.product_id.supplier_taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            line.taxes_id = fpos.map_tax(taxesRec, line.product_id, line.order_id.partner_id) if fpos else taxesRec

    order_line_ref = fields.Char()
    final_sales_price = fields.Float('Final Sales Price')
    available_size = fields.Char('Available Size')
    colours = fields.Integer('Colours')
    product_specification = fields.Char()


    @api.multi
    def write(self, vals):
        tax = self.env['account.tax']
        taxesRec = self.env['account.tax']
        sol = self.env['sale.order.line'].search([
            ('id', '=', self.order_line_ref)])
        if sol and vals.get('taxes_id') and not self.env.context.get('from_so'):
            tax_ids = tax.search([
                ('id', 'in', vals['taxes_id'][0][2])])
            for tax in tax_ids:
                taxIds = tax.search([
                    ('description', '=', tax.description),
                    ('type_tax_use', '=', 'sale'),
                    ('company_id', '=', vals.get('company_id') or self.company_id.id)])
                taxesRec += taxIds
            sol.with_context(from_po=True).write({
                'tax_id': [(6, 0, taxesRec.ids)]
                })
        return super(PurchaseOrderLine, self).write(vals)




class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    final_sales_price = fields.Float(string='Final Sales Price')
    available_size = fields.Char('Available Size')
    colours = fields.Integer('Colours')
    product_specification = fields.Char()
    website_product_qty = fields.Float(related='product_id.website_product_qty', string='Website Product Available')

    @api.multi
    def unlink(self):
        if self:
            purchase_lines = self.env['purchase.order.line']
            purchase_order_line = purchase_lines.search([('order_line_ref','=',self.id)])
            if self.product_uom_qty == 0.0 and \
               purchase_order_line and \
               purchase_order_line.state in ['purchase', 'done']:
               purchase_order_line.product_qty = 0.0
            elif purchase_order_line:
                purchase_order_line.unlink()
        return super(SaleOrderLine, self).unlink()

    @api.model
    def create(self,vals):
        res = super(SaleOrderLine,self).create(vals)
        company = self.env['res.company']
        purchase = self.env['purchase.order']
        purchase_lines = self.env['purchase.order.line']
        taxes = self.env['account.tax']
        company_id = company.search([('partner_id','=',res.order_id.partner_id.id)])
        res.final_sales_price = vals.get('final_sales_price') or res.product_id.final_sales_price
        res.available_size = vals.get('available_size') or res.product_id.available_size
        res.colours = vals.get('colours') or res.product_id.colours

        # website_product_qty update
        if res.product_id:
            product_tmp_id = res.product_id.product_tmpl_id
            product_tmp_id.get_website_product_qty()

        if company_id.parent_id.id:
            purchase_order = purchase.search([('so_reference','=',res.order_id.id)])
            taxes_ids = res.product_id.supplier_taxes_id.ids
            # order from website
            if purchase_order:
                # names = []
                # tax = False
                # for tax in res.product_id.supplier_taxes_id:
                #     names.append(tax.name)
                # tax_ids = taxes.search(['&',('name','in',names),
                #                         '&',('type_tax_use','=','purchase'),
                #                         ('company_id','=',company_id.id)])
                purchase_order_line = purchase_lines.create({
                                                    'name' : res.name,
                                                    'order_id' : purchase_order.id,
                                                    'order_line_ref' : res.id,
                                                    'product_id' : res.product_id.id,
                                                    'product_qty' : res.product_uom_qty,
                                                    'price_unit' : res.price_unit,
                                                    'product_uom' : res.product_uom.id,
                                                    'final_sales_price': vals.get('final_sales_price') or res.product_id.final_sales_price,
                                                    'available_size': vals.get('available_size') or res.product_id.available_size,
                                                    'colours': vals.get('colours') or res.product_id.colours,
                                                    # 'taxes_id' : [(6, 0, tax_ids.ids)],
                                                    'date_planned': res.create_date,
                                                    'product_specification': res.product_specification,
                                                    })
                purchase_order._compute_tax_id()
            else:
                res.order_id.sale_order_check = False
        return res

    @api.multi
    def write(self,vals):
        # print("sol write=========================",vals)

        res = super(SaleOrderLine,self).write(vals)
        purchase_line = self.env['purchase.order.line']

        # website_product_qty code
        if vals.get('product_uom_qty') or vals.get('qty_delivered'):
            product_tmp_id = self.product_id.product_tmpl_id
            product_tmp_id.get_website_product_qty()

        pol = purchase_line.search([('order_line_ref','=',self.id)])
        tax = self.env['account.tax']
        taxesRec = self.env['account.tax']
        if vals.get('tax_id') and not self.env.context.get('from_po'):
            tax_ids = tax.search([
                ('id', 'in', vals['tax_id'][0][2])])
            for tax in tax_ids:
                taxIds = tax.search([
                    ('description', '=', tax.description),
                    ('type_tax_use', '=', 'purchase'),
                    ('company_id', '=', vals.get('company_id') or self.company_id.id)])
                taxesRec += taxIds

        # print("taxesRec===============",taxesRec, pol, pol.taxes_id)
        if pol:
            pol.with_context(from_so=True).write({
                    'name' : self.name,
                    'product_id':self.product_id.id,
                    'product_specification': self.product_specification,
                    'product_qty' : self.product_uom_qty,
                    'price_unit' : self.price_unit,
                    'product_uom' : self.product_uom.id,
                    'final_sales_price': vals.get('final_sales_price') or self.final_sales_price,
                    'available_size': vals.get('available_size') or self.available_size,
                    'colours': vals.get('colours') or self.colours,
                    'date_planned': self.create_date,
                    'taxes_id': [(6,0,taxesRec.ids)]
                    })
        return res

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine,self).product_id_change()
        self.final_sales_price = self.product_id.final_sales_price
        self.available_size = self.product_id.available_size
        self.colours = self.product_id.colours
        return res

class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_check = fields.Boolean(default=True)
    credit_limit = fields.Float('Current Credit Limit', compute='_compute_credit_limit')
    is_picking = fields.Boolean(string='Is Picking')
    mobile = fields.Char(
        string='Mobile No.', related='partner_id.mobile',
        readonly=True, copy=False)
    state_id = fields.Many2one(
        'res.country.state', string='State', related='partner_id.state_id', store=True)
    is_confirm = fields.Boolean(string='Is Confirm?')

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': round(order.pricelist_id.currency_id.round(amount_untaxed + amount_tax))
            })

    @api.multi
    def check_credit_limit(self, partner, sale_domain):
        PaymentObj = self.env['account.payment']
        send_money, receive_money, total_sales= 0.0, 0.0, 0.0
        receive_money = sum([x['amount']
                                for x in PaymentObj.sudo().search_read(
                                    ['&',('partner_id', '=', partner.id),
                                    '&',('payment_type','like','inbound'),
                                        ('state', '=', 'posted')],
                                    fields=['amount'])])
        send_money = sum([x['amount']
                            for x in PaymentObj.sudo().search_read(
                                ['&',('partner_id', '=', partner.id),
                                '&',('payment_type','like','outbound'),
                                    ('state', '=', 'posted')],
                                fields=['amount'])])
        total_sales = sum([x['amount_total']
                            for x in self.sudo().search_read(
                                sale_domain,fields=['amount_total'])])
        credit = receive_money - send_money
        return credit, total_sales

    @api.multi
    def order_confirmation_cron(self):
        sale_orders = self.env['sale.order'].search([('state', 'in', ['draft', 'sent']), ('is_confirm', '=', True)])
        for sale in sale_orders:
            sale.action_confirm()

    @api.multi
    def quotation_cancel_cron(self):
        """ Quatation order cancel after 7 days of creation date """

        remove_date = datetime.datetime.today() - datetime.timedelta(days=7)
        remove_date = remove_date.strftime('%Y-%m-%d %H:%M:%S')
        QuotFileIds = self.search([('state', '=', 'draft'), ('create_date', '<', remove_date)])
        for quote in QuotFileIds:
            quote.action_cancel()

    @api.multi
    def _compute_credit_limit(self):
        for order in self:
            partner = order.partner_id
            total_credit,total_sales = order.check_credit_limit(partner,
                                                            ['&',('partner_id', '=', partner.id),
                                                            ('state', 'in', ['sale','done'])])
            customer_credit = total_credit + partner.credit_limit_custom
            print("total_credit,total_sales =================",total_credit,total_sales,customer_credit,partner.credit_limit_custom)
            order.credit_limit = customer_credit - total_sales
        return True

    @api.multi
    def set_sequence(self, company_id):
        sequence = ''
        if company_id:
                sequence = self.env['ir.sequence'].with_context(
                    force_company=company_id).next_by_code('sale.order') or _('New')
        else:
            sequence = self.env['ir.sequence'].next_by_code('sale.order') or _('New')
        return sequence

    @api.multi
    def write(self,vals):
        # Be careful if write method called from lambda then self contain false values
        if vals.get('state') == 'sent':
            vals['date_order'] = fields.datetime.now()
            if 'company_id' in vals:
                sequence = self.set_sequence(vals['company_id'])
                vals['name'] = sequence
            elif self.company_id:
                vals['name'] = self.set_sequence(self.company_id.id)
            else:
                vals['name'] = self.set_sequence(False)
                # vals['name'] : self.set_sequence(False)

        if vals.get('state') == 'sale' and (not self.name or self.name == 'Quote'):
            if 'company_id' in vals:
                sequence = self.set_sequence(vals['company_id'])
                vals['name'] = sequence
            elif self.company_id:
                vals['name'] = self.set_sequence(self.company_id.id)
            else:
                vals['name'] = self.set_sequence(False)
        ''' search company partner if order come from outlet user from website,
            and update note,payment term and fiscal position on po'''

        _logger.info('write vals: %s', vals)
        if vals.get('partner_id'):
            partner = self.env['res.partner'].search([('id','=',vals['partner_id'])])
            if partner.company_id.parent_id.id:
                vals.update({'partner_id':partner.company_id.partner_id.id})
        if vals.get('user_id') == 1:
            vals.update({'user_id' : False})
        res = super(SaleOrder,self).write(vals)
        # website_product_qty code
        if vals.get('state'):
            for line in self.order_line:
                product_tmp_id = line.product_id.product_tmpl_id
                product_tmp_id.get_website_product_qty()

        if 'note' in vals or 'fiscal_position_id' in vals or 'payment_term_id' in vals:
            purchase_order = self.env['purchase.order'].search([('so_reference','=',self.id)])
            if purchase_order:
                fiscal_position = self.env['account.fiscal.position'].search(['&',('name','=',self.fiscal_position_id.name),
                                                             ('company_id','=',purchase_order.company_id.id)],limit=1)
                purchase_order.notes = self.note
                purchase_order.payment_term_id = self.payment_term_id.id or False
                purchase_order.write({'fiscal_position_id' : fiscal_position.id or False})
                purchase_order._compute_tax_id()
        return res

    @api.model
    def create(self,vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].\
                with_context(force_company=vals['company_id']).\
                next_by_code('quotation.order') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].\
                next_by_code('quotation.order') or _('New')
        partner = self.env['res.partner']
        company = self.env['res.company']
        purchase_order = self.env['purchase.order']
        purchase_lines = self.env['purchase.order.line']
        warehouse_obj = self.env['stock.warehouse']
        taxes = self.env['account.tax']
        fiscal_position = self.env['account.fiscal.position']
        partner_id = partner.search([('id','=',vals['partner_id'])])
        if partner_id.company_id.parent_id.id:
            vals.update({'partner_id':partner_id.company_id.partner_id.id,
                         'partner_shipping_id':partner_id.company_id.partner_id.id,
                         'partner_invoice_id':partner_id.company_id.partner_id.id,
                         'user_id' : False})
        res = super(SaleOrder,self).create(vals)
        company_id = company.search([('partner_id','=',res.partner_id.id)])
        if company_id.parent_id.id:
            location_id = False
            fiscal_position_id = fiscal_position.search(['&',('name','=',res.fiscal_position_id.name),
                                                             ('company_id','=',company_id.id)],limit=1)
            warehouse_id = warehouse_obj.search([('company_id', '=', company_id.id)])
            for warehouse in warehouse_id:
                location_id = warehouse.in_type_id.id
            order = purchase_order.create({
                                'partner_id' : res.company_id.partner_id.id or False,
                                'fiscal_position_id' : fiscal_position_id.id or False,
                                'payment_term_id' : res.payment_term_id.id or False,
                                'company_id' : company_id.id or False,
                                'date_order' : res.date_order,
                                'so_reference' : res.id,
                                'picking_type_id' : location_id,
                                'notes' : res.note
                                })
            if res.sale_order_check == False:
                for line in res.order_line:
                    names = []
                    tax = False
                    for tax in line.product_id.supplier_taxes_id:
                        names.append(tax.name)
                    tax_ids = taxes.search(['&',('name','in',names),
                                            '&',('type_tax_use','=','purchase'),
                                            ('company_id','=',company_id.id)])
                    purchase_lines.create({
                                            'name' : line.name,
                                            'order_id' : order.id,
                                            'order_line_ref' : line.id,
                                            'product_id' : line.product_id.id,
                                            'product_qty' : line.product_uom_qty,
                                            'price_unit' : line.price_unit,
                                            'product_uom' : line.product_uom.id,
                                            'final_sales_price': line.final_sales_price,
                                            'available_size': line.available_size,
                                            'colours': line.colours,
                                            'date_planned': line.create_date,
                                            # 'taxes_id' : [(6, 0, tax_ids.ids)],
                                            'product_specification': line.product_specification,
                                        })
                order._compute_tax_id()
        return res

    @api.multi
    def po_action_quoation_send(self, purchase_order):
        if purchase_order:
            purchase_order.write({'state':'sent',
                                  'date_order' : fields.datetime.now(),
                                  })
        return True

    @api.multi
    def action_quotation_send(self):
        res = super(SaleOrder,self).action_quotation_send()
        # self.write({'date_order' : fields.datetime.now()})
        purchase_order = self.env['purchase.order'].search([('so_reference','=',self.id)])
        self.po_action_quoation_send(purchase_order)
        return res

    @api.multi
    def force_quotation_send(self):
        res = super(SaleOrder,self).force_quotation_send()
        # self.write({'date_order' : fields.datetime.now()})
        purchase_order = self.env['purchase.order'].search([('so_reference','=',self.id)])
        self.po_action_quoation_send(purchase_order)
        return res

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder,self).action_cancel()
        purchase = self.env['purchase.order']
        purchase_order = purchase.search([('so_reference','=',self.id)])
        if purchase_order:
            purchase_order.write({'state':'cancel'})
        return res

    @api.multi
    def action_draft(self):
        res = super(SaleOrder,self).action_draft()
        purchase = self.env['purchase.order']
        purchase_order = purchase.search([('so_reference','=',self.id)])
        if purchase_order:
            purchase_order.write({'state':'draft'})
        return res

    @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent',
                                                            'date_order' : fields.datetime.now(),
                                                          })
        purchase_order = self.env['purchase.order'].search([('so_reference','=',self.id), ('state','=','draft')])
        self.po_action_quoation_send(purchase_order)
        return self.env.ref('caret_united18_custom.report_gst_sale_menu').report_action(self)

    @api.multi
    def check_limit(self):
        self.ensure_one()
        partner = self.partner_id
        order_amount = self.amount_total
        total_credit,total_sales = self.check_credit_limit(partner,
                                                            ['&',('partner_id', '=', partner.id),
                                                            ('state', 'in', ['sale','done'])])
        total = total_sales + order_amount
        customer_credit = total_credit + partner.credit_limit_custom
        if total > customer_credit:
            msg = 'Can not confirm Sale Order,Total mature due Amount ' \
                  '%s as on %s !\nCheck Partner Accounts or Credit ' \
                  'Limits !' % (order_amount, customer_credit - total_sales)
            raise UserError(_('Credit Over Limits !\n' + msg))
        return True

    def action_confirm(self):
        self.ensure_one()
        purchase = self.env['purchase.order']
        purchase_order = purchase.search([('so_reference','=',self.id)])
        if self.payment_term_id.name != 'Immediate Payment':
            for order in self:
                order.check_limit()
        res = super(SaleOrder, self).action_confirm()
        purchase_order.sudo().button_confirm()
        sms_template = self.env['ir.model.data'].get_object('caret_sms', 'sale_order_sms_template')
        sms_rendered_content = self.env['sms.body.template'].render_template(sms_template.template_body, sms_template.model, self.id)
        api_key = self.env['ir.config_parameter'].sudo().get_param('caret_sms.textlocal_api_key')
        sender = self.env['ir.config_parameter'].sudo().get_param('caret_sms.sender')
        to_number = ''
        to_mobile = self.partner_id.mobile or self.partner_id.phone
        if to_mobile:
            if len(to_mobile) == 10:
                to_number = str(91) + to_mobile
            elif '+' in to_mobile and len(to_mobile) == 13:
                to_number = to_mobile.replace('+','').strip()
            elif '+' in to_mobile and len(to_mobile) == 11:
                to_number = to_mobile.replace('+','').strip()
            elif '+' in to_mobile and len(to_mobile) == 11:
                to_number = to_mobile.replace('+','').strip()
            else:
                to_number = self.partner_id.mobile
            SMS_record = self.env['sms.sms'].create({'textlocal_api_key':api_key,
                                        'to_number': to_number,
                                        'message': sms_rendered_content,
                                        'sender': sender,
                                        'res_id': self.id or False,
                                        'res_model': 'sale.order',
                                        })
            SMS_record.sendSMS()
        return res
    
    @api.multi
    def _get_cgst_tax_rate_amount(self):
        res = []
        amount = 0
        for line in self.order_line:
            for tax in line.tax_id:
                if 'CGST' in tax.name:
                    amount = amount + line.price_subtotal*tax.amount/100
                elif tax.children_tax_ids:
                    amount = amount + line.price_subtotal*tax.children_tax_ids[0].amount/100
        res.append ({
                    'amount': amount,
                    })
        return res

    @api.multi
    def _get_sgst_tax_rate_amount(self):
        res = []
        amount = 0
        for line in self.order_line:
            for tax in line.tax_id:
                if 'SGST' in tax.name:
                    amount = amount + line.price_subtotal*tax.amount/100
                elif tax.children_tax_ids:
                    amount = amount + line.price_subtotal*tax.children_tax_ids[1].amount/100
        res.append ({
                    'amount': amount,
                    })
        return res

    @api.multi
    def _get_igst_tax_rate_amount(self):
        res = []
        amount = 0
        for line in self.order_line:
            for tax in line.tax_id:
                if 'IGST' in tax.name:
                    amount = amount + line.price_subtotal*tax.amount/100
        res.append ({
                    'amount': amount,
                    })
        return res

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = self.currency_id.amount_to_text(amount)
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words

