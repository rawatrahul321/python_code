from odoo import models, fields, api
from odoo.tools.translate import _
from odoo import api, fields, models, tools, SUPERUSER_ID, _
import datetime

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError
import math
import odoo.addons.decimal_precision as dp


class OrderForm(models.Model):
    _name = 'order.form'
    _order = 'write_date'
    _inherit = 'mail.thread'
    _description = "Customer Order Form"
    
    @api.onchange('customer_id')
    def get_location(self):
        self.location_value = self.customer_id.location.name

    
    @api.depends('customer_id')
    @api.one
    def get_credit_limit(self):
        print '** Credit Limit **',self.customer_id.credit_limit
        self.credit_limit = self.customer_id.credit_limit
        self.balance_credit = self.credit_limit - self.customer_id.credit
        self.sales_person = self.customer_id.user_id
        
    @api.multi
    def check_limit(self):
        """Check if credit limit for partner was exceeded."""
        self.ensure_one()
        partner = self.customer_id
        moveline_obj = self.env['account.move.line']
        movelines = moveline_obj.\
            search([('partner_id', '=', partner.id),
                    ('account_id.user_type_id.type', 'in',
                    ['receivable', 'payable']),
                    ('full_reconcile_id', '=', False)])

        debit, credit = 0.0, 0.0
        today_dt = datetime.strftime(datetime.now().date(), '%d-%m-%y')
        for line in movelines:
            if line.date_maturity < today_dt:
                credit += line.debit
                debit += line.credit

        if (credit - debit + self.amount_total) > partner.credit_limit:
            # Consider partners who are under a company.
            if partner.over_credit or (partner.parent_id
                                       and partner.parent_id.over_credit):
                partner.write({
                    'credit_limit': credit - debit + self.amount_total})
                return True
            else:
                print 'OVER CREDIT+++++++',partner.over_credit
                print 'CR - DB++++++++',partner.credit , partner.debit
                msg = '''Cannot Confirm Order, Total Mature Due Amount is
                  Rs. %s as on %s !\nCheck Partner Accounts or Credit Limits !''' % (partner.credit - partner.debit, today_dt)
                raise UserError(_('Credit Over Limits !\n' + msg))
        else:
            return True

    
    name = fields.Char(string='Code', size=25, readonly=True)
    customer_id = fields.Many2one('res.partner',string='Customer',required=True,default=lambda self: self.env.user.partner_id)
    date_order = fields.Datetime('Order Date')
    user_id = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)
    order_ids = fields.One2many('order.form.line','order_id','Order Line')
    state = fields.Selection([
       ('draft', 'Draft Order'),
       ('sent', 'Draft Order Sent'),
       ('done', 'Approved'),
       ('cancel', 'Cancelled'),
    ],  string='Order Status', readonly=True, copy=False, store=True, default='draft')
    payment_term_id = fields.Many2one('account.payment.term','Payment Term')
    expiration_date = fields.Date('Expiration Date')
    notes = fields.Char('Notes')
    amount_total = fields.Monetary('Total Amount  (Excluding Tax)',compute='_amount_all',store=True,default=False)
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env.user.company_id.currency_id)
    credit_limit = fields.Float('Credit Limit',compute='get_credit_limit',store=True,default=False)
    balance_credit = fields.Float('Balance Credit',compute='get_credit_limit',store=True,default=False)
    sales_person = fields.Many2one('res.users','Salesperson')
    truck_type = fields.Many2one('truck.details','Truck Type',domain="[('location.name','=',location_value)]")
    total_volume = fields.Float('Ordered Volume',help='Total Volume i.e. Total Volume To be consumed by Ordered Quantity.')
    balance_volume = fields.Float('Balance Volume')
    location_value = fields.Char('Customer Location',store=True,default=False)
    
    @api.onchange('truck_type','total_volume')
    def get_volume(self):
        if self.truck_type:
            self.balance_volume = self.truck_type.volume - self.total_volume
            
    @api.multi
    def button_dummy(self):
        return True
    
    @api.multi
    def sent_quot(self):
        for order in self:
            order.check_limit()
        self.write({'state':'sent'})
        
    @api.multi
    def draft(self):
        self.write({'state':'draft'})
    
    @api.one
    def create_sale_order(self):   
        list_sale_order_line = []
        for line in self.order_ids:
            art = {}
            art['product_id'] = line.product_id.id
            art['name'] = line.product_id.name
            art['product_uom_qty'] = line.updated_qty                
            art['discount'] = line.discount
            art['list_price'] = line.unit_price
            art['product_uom'] = 1
             
            list_sale_order_line.append((0, 0, art))
        
        vals = {
            'state': 'draft',
            'date_order': self.date_order,
            'date_create': self.date_order,
            'user_id': self.user_id.id,
            'partner_id': self.customer_id.id,
            'order_policy': 'manual',
            'active':True,
            'payment_term_id':self.payment_term_id.id,
            'note':self.notes,
            'order_line' : list_sale_order_line
        }
    
        res = self.env['sale.order'].create(vals)
        self.write({'state':'done'})
        return res
    
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('order.form') or '/'
        vals['name'] = seq
        return super(OrderForm, self).create(vals)
    
    @api.depends('order_ids.sub_total')
    def _amount_all(self):
        """
        Compute the total amounts of the Order Form.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            volume_total = 0.0
            for line in order.order_ids:
                amount_untaxed += line.sub_total
                volume_total += line.volume
                # FORWARDPORT UP TO 10.0
#                 if order.company_id.tax_calculation_rounding_method == 'round_globally':
#                     price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#                     taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)
#                     amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
#                 else:
#                     amount_tax += line.price_tax
            order.update({
#                 'amount_untaxed': order.round(amount_untaxed),
#                 'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed,
                'total_volume': volume_total
            })
   
class OrderFormLine(models.Model):
    _name = 'order.form.line'
    
    @api.depends('product_id')
    @api.one
    def compute_discount(self):
        self.discount = self.product_id.discount
        self.unit_price = self.product_id.list_price
    
    @api.depends('updated_qty')
    @api.one
    def compute_subtotal(self):
        self.sub_total = (self.unit_price * self.updated_qty) * (1 - (self.discount or 0.0) / 100.0)
        print 'Sub Total With Updated Qty++',self.sub_total
        
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id :
            self.name = self.product_id.default_code
            self.volume = self.product_id.volume
    
    @api.depends('quantity')
    @api.one
    def get_prev_qty(self):
        self.updated_qty = self.quantity
    
    @api.depends('product_id')
    @api.one 
    def get_carton_details(self):
        self.outer_carton = self.product_id.outer_carton
        self.inner_carton = self.product_id.inner_carton   
    
    @api.onchange('total_qty')
    def get_ordered_qty(self):
        value = 0
        rem = 0
        for line in self:
            print 'Total Quantity After Multiply +++++',line.inner_carton, line.outer_carton, line.total_qty
            value = line.inner_carton * line.outer_carton
            if line.total_qty and value > 0:
                rem = line.total_qty % value
                print '** Value **',value
                if line.total_qty <= value:
                    print '** Total Quantity Lesser than Value **'
                    self.quantity = value
                if line.total_qty > value:
                    print '** REMAINDER Value **',rem
                    if rem >= value/2:
                        print '** Greater Than Entry **'
                        self.quantity = (self.total_qty - rem) + value
                        print '** Quantity **',self.quantity
                    if rem < value/2:
                        print '** Lesser Entry **'
                        self.quantity = self.total_qty - rem
                        print '** Quantity ++++',self.quantity
        
    name = fields.Char('Product Code',required=True)
    order_id = fields.Many2one('order.form','Order Id')
    product_id = fields.Many2one('product.product', string='Product Name / Code', required=True,domain=[('sale_ok', '=', True)])
    quantity = fields.Integer('Ordered Quantity as per (PR)')
    discount = fields.Float('Discount (%)',compute='compute_discount',store=True,default=False)
    unit_price = fields.Float('Unit Price',compute='compute_discount',store=True,default=False)
    sub_total = fields.Float('Sub Total',compute='compute_subtotal',store=True,default=False)
    update_check = fields.Boolean('Updated')
    updated_qty = fields.Float('Updated Quantity',compute='get_prev_qty',store=True,default=False, digits=dp.get_precision('Updated Quantity'))
    outer_carton = fields.Integer('No. Of Outer Cartons',compute= 'get_carton_details',store=True,default=False)
    inner_carton = fields.Integer('No. Of Inner Cartons',compute= 'get_carton_details',store=True,default=False)
    total_qty = fields.Integer('Input Quantity')
    volume = fields.Float('Volume')
    packing_standard = fields.Char('Packing Standard (PR)')
    unit_type = fields.Selection([('sets','Sets'),('piece','Per Piece')],string="Unit Type",default="sets")
    
    @api.onchange('product_id')
    def get_packing_standard(self):
        a = self.product_id.inner_carton
        b = self.product_id.outer_carton
        if self.product_id:
            self.packing_standard  = str(a) + " * " + str(b)
            
class ProductProduct(models.Model):
    _inherit = "product.product"

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    discount = fields.Float('Discount (%)')
    carton_select = fields.Selection([('in','Inner Carton'),('out','Outer Carton')],string="Select Carton")
    outer_carton = fields.Integer('No. Of Outer Carton',default = 1)
    inner_carton = fields.Integer('No. Of Inner Carton',default = 1)
    
    inner_carton_qty = fields.Integer('Items in Inner Carton',default=1)
    group_product = fields.Boolean("Is a Group Of Product")
    no_of_component = fields.Integer("No. Of Sub-Component")
    prod_attribute = fields.Char("Attribute Name",help="For Shells Like Left, Right & Center")
    prod_color = fields.Char('Color')    
    
class TruckType(models.Model):
    _name = 'truck.details'
    
    name = fields.Char('Truck Name')
    volume = fields.Float('Volume',help='Total Volume Of Truck')        
    location = fields.Many2one('truck.location','Truck Location')

class TruckLocation(models.Model):
    _name = 'truck.location'
    
    name = fields.Char('Location')

class Partner(models.Model):
    _inherit = 'res.partner'    
    
    location = fields.Many2one('truck.location','Location')







        