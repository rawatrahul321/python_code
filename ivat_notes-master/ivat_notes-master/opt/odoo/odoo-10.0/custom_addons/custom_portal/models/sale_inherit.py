from odoo import models, fields, api
from odoo.tools.translate import _
import datetime
import odoo.addons.decimal_precision as dp
from odoo.tools import float_is_zero, float_compare
import json
from odoo.exceptions import UserError, ValidationError
import string

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.depends('partner_id')
    def getValue(self):
        if self.partner_id:
            self.list_discount_percentage = str(self.partner_id.discount) + '%'
            self.breakage_discount_percentage = str(self.partner_id.breakage) + '%'
            self.truck_discount_percentage = str(self.partner_id.truck_load) + '%'
    
    def get_discount(self):
        print 'ENtry Discount======',self.partner_id.discount
        breakage_percent = 0.0
        truck_load_percent = 0.0
        freight_percent = 0.0
        if self.partner_id:
            self.list_discount = ((self.amount_untaxed) * self.partner_id.discount) / 100
            breakage_percent = self.partner_id.breakage
            self.breakage_discount = (self.amount_untaxed - self.list_discount) * breakage_percent / 100   
            truck_load_percent = self.partner_id.truck_load
            self.truck_load_discount = ((self.amount_untaxed) - (self.list_discount +  self.breakage_discount)) * truck_load_percent / 100 
            
        return True
    
    @api.one
    @api.depends('order_line.price_total','freight_charge','tax_id','amount_untaxed')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                    print 'amount tax$$$$',amount_tax
                else:
                    amount_tax += line.price_tax
                    print 'amount tax@@@@@@@',amount_tax
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                
            })
            total_amount = (amount_untaxed) - (self.list_discount + self.breakage_discount + self.truck_load_discount) + self.freight_charge
            discountTotal = (self.list_discount + self.breakage_discount + self.truck_load_discount + self.freight_charge)
            taxAmount = (total_amount * self.tax_id.amount / 100)
            print '***********Total Amount++++',total_amount,taxAmount
            print 'Discount Total-----',discountTotal
            order.update({
                'discount_amount': discountTotal,
                'sub_total': total_amount,
                'taxAmount': order.pricelist_id.currency_id.round(taxAmount),
                'amount_total': total_amount + taxAmount,
                'total_quantity': int(sum(line.product_uom_qty for line in self.order_line))
                })
            
    
    
    list_discount_percentage = fields.Char("List Discount Percent",compute='getValue',store=True,default=False)
    list_discount = fields.Monetary('List Less Discount',compute='get_discount')
    
    breakage_discount = fields.Monetary('Breakage Discount',compute='get_discount')
    breakage_discount_percentage = fields.Char("Breakage Discount Percent",compute='getValue',store=True,default=False)
    
    truck_load_discount = fields.Monetary('Truck Load',compute='get_discount')
    truck_discount_percentage = fields.Char("Truck Load Discount Percent",compute='getValue',store=True,default=False)
    
    freight_charge = fields.Monetary('Freight')
    sub_total = fields.Monetary('Sub-Total',compute='_amount_all')
    tax_id = fields.Many2one('account.tax', string='Tax', domain=[('type_tax_use', '=', 'sale')])
    taxAmount = fields.Monetary(string='Tax Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    discount_amount = fields.Float('Total Discount',compute='_amount_all',store=True,default=False)
    
    total_quantity = fields.Float('Total Quantity',compute='_amount_all',store=True,default=False)
    
    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'tax_id': self.tax_id.id,
            'freight_charge': self.freight_charge,
            'discount_amount': self.discount_amount,
            'total_quantity': self.total_quantity,
        }
        return invoice_vals
    
class Partner(models.Model):
    _inherit = "res.partner"
    
    discount = fields.Float("Discount (%)",help='Custom Discount Based On Customer')
    breakage = fields.Float("Breakage (%)")
    truck_load = fields.Float("Truck Load (%)")
    
class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    
    @api.one
    def get_discount(self):
        breakage_percent = 0.0
        truck_load_percent = 0.0
        freight_percent = 0.0
        if self.partner_id:
            self.list_discount = ((self.amount_untaxed) * self.partner_id.discount) / 100
            breakage_percent = self.partner_id.breakage
            self.breakage_discount = (self.amount_untaxed - self.list_discount) * breakage_percent / 100   
            truck_load_percent = self.partner_id.truck_load
            self.truck_load_discount = ((self.amount_untaxed) - (self.list_discount +  self.breakage_discount)) * truck_load_percent / 100 
            
        return True
    
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type','freight_charge','sub_total','tax_id','amount_untaxed')              
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids)
    
        
        total_amount = (self.amount_untaxed) - (self.list_discount + self.breakage_discount + self.truck_load_discount + self.freight_charge) 
        discountTotal = (self.list_discount + self.breakage_discount + self.truck_load_discount + self.freight_charge)

        self.discount_amount = discountTotal
        self.taxAmount = (total_amount * self.tax_id.amount / 100)
        self.sub_total = total_amount
        self.amount_total = self.sub_total + self.taxAmount
    
    list_discount_percent = fields.Float("List Discount Percent")
    list_discount = fields.Monetary('List Less Discount',compute='get_discount')
    breakage_discount = fields.Monetary('Breakage Discount',compute='get_discount')
    truck_load_discount = fields.Monetary('Truck Load',compute='get_discount')
    freight_charge = fields.Monetary('Freight')
    sub_total = fields.Monetary('Sub-Total',compute='_compute_amount',store=True,default=False)
    tax_id = fields.Many2one('account.tax', string='Tax', domain=[('type_tax_use', '=', 'sale')])
    taxAmount = fields.Monetary(string='Tax Amount', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    discount_amount = fields.Float('Total Discount',compute='_compute_amount',store=True,default=False)
    
    amount_total = fields.Monetary(string='Total',
        store=True, readonly=True, compute='_compute_amount')
    
    total_quantity = fields.Float('Total Quantity')

    @api.model
    def invoice_line_move_line_get(self):
        amount_discount = 0.0
        ks_res = super(AccountInvoice, self).invoice_line_move_line_get()
        amount_discount = (self.list_discount + self.breakage_discount + self.truck_load_discount + self.freight_charge)
        
        if amount_discount > 0:
            ks_name = "Global Discount"
            discount_account = self.env['account.account'].search([('name','=','Transfer Account')])
            
            if (self.type == "out_invoice" or self.type == "out_refund"):
                dict = {
                    'invl_id': self.number,
                    'type': 'src',
                    'name': ks_name,
                    'price_unit': amount_discount,
                    'quantity': 1,
                    'price': -amount_discount,
                    'account_id': discount_account.id,
                    'invoice_id': self.id,
                }
                ks_res.append(dict) 
        return ks_res
    
    # TAX LINE
    @api.model
    def tax_line_move_line_get(self):
        ks_res = super(AccountInvoice, self).tax_line_move_line_get()
 
        if self.taxAmount > 0:
            ks_name = "Global Tax"
            tax_account = self.env['account.account'].search([('name','=','Sales Tax Payable')])
             
            if (self.type == "out_invoice" or self.type == "out_refund"):
                dict = {
                    'invl_id': self.number,
                    'type': 'src',
                    'name': ks_name,
                    'price_unit': self.taxAmount,
                    'quantity': 1,
                    'price': self.taxAmount,
                    'account_id': tax_account.id,
                    'invoice_id': self.id,
                }
                ks_res.append(dict)   
                print 'ks_res0000000000000'  ,ks_res   
        return ks_res
