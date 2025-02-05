from odoo import models, fields, api, _
import convertion
from pygments.lexer import _inherit
from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import amount_to_text_en, float_round
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    weight = fields.Float('Weight')
    packages = fields.Char('Packages')
    gr_no = fields.Char('G.R. No.')
    transporter = fields.Many2one('transporter.details','Transporter')
    party_code = fields.Char('Party Code')
    gr_date = fields.Date('G.R. Date')
    dispatch_through = fields.Char('Dispatched Through')
    vehicle_no = fields.Char('Vehicle Number')
  
    @api.multi
    @api.depends('taxAmount')
    def get_tax_amount_letter(self):
        amount = convertion.trad(int(self.taxAmount),'')
        return amount
    
    @api.multi
    @api.depends('amount_total')
    def get_amount_letter(self):
        amount = convertion.trad(int(self.amount_total),'')
        return amount
    
class TransporterDetails(models.Model):
    _name = "transporter.details"
    
    name = fields.Char('Name')
    address = fields.Char('Address')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hs_code = fields.Char(string="HSN Code")


class AccountInvoiceLineInherit(models.Model):
    _inherit = "account.invoice.line"
    
    HsnCode = fields.Char('HSN Code')
    DiscountAmount = fields.Float('Discount Amount',compute = 'get_discount',store=True,default=False)
        
    @api.one
    @api.depends('discount')
    def get_discount(self):
        for line in self:
            if line.price_unit:
                print 'Unit Price++++', line.price_unit, line.discount
                self.DiscountAmount = (line.price_unit * line.discount)/100
                print '++Discount Amount++',self.DiscountAmount
        return self.DiscountAmount
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = {}
        if not self.invoice_id:
            return

        part = self.invoice_id.partner_id
        fpos = self.invoice_id.fiscal_position_id
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        type = self.invoice_id.type

        if not part:
            warning = {
                    'title': _('Warning!'),
                    'message': _('You must first select a partner!'),
                }
            return {'warning': warning}

        if not self.product_id:
            if type not in ('in_invoice', 'in_refund'):
                self.price_unit = 0.0
            domain['uom_id'] = []
        else:
            if part.lang:
                product = self.product_id.with_context(lang=part.lang)
            else:
                product = self.product_id

            self.name = product.partner_ref
            self.HsnCode = product.hs_code
            account = self.get_invoice_line_account(type, product, fpos, company)
            if account:
                self.account_id = account.id
            self._set_taxes()

            if type in ('in_invoice', 'in_refund'):
                if product.description_purchase:
                    self.name += '\n' + product.description_purchase
            else:
                if product.description_sale:
                    self.name += '\n' + product.description_sale

            if not self.uom_id or product.uom_id.category_id.id != self.uom_id.category_id.id:
                self.uom_id = product.uom_id.id
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

            if company and currency:
                if company.currency_id != currency:
                    self.price_unit = self.price_unit * currency.with_context(dict(self._context or {}, date=self.invoice_id.date_invoice)).rate

                if self.uom_id and self.uom_id.id != product.uom_id.id:
                    self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)
        return {'domain': domain}
    
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.multi
    def amount_to_text(self, amount, currency='INR'):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='Rupees')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words
    
    
class StockMove(models.Model):
    _inherit = 'stock.move'
    
    unit_price = fields.Float('Unit Price')
    amount = fields.Float('Amount')
    product_code = fields.Char('Product Code')
    
    @api.one
    def push_price(self):
        print 'HELLO PUSH++++++'
        code = ''
        price = 0.0
        total_amount = 0.0
        for move in self:
            
            if move.procurement_id and move.procurement_id.sale_line_id:
                sale_lines = move.procurement_id.sale_line_id  
                print 'SALE LINE ID+++++++++',sale_lines.price_unit
                print 'Product CODE+++++++',sale_lines.product_id.hs_code
                price = sale_lines.price_unit
                code = sale_lines.product_id.hs_code
                total_amount = price * sale_lines.product_uom_qty
        self.product_code = code
        self.unit_price = price
        self.amount = total_amount
    
    @api.multi
    def action_confirm(self):
        """ Confirms stock move or put it in waiting if it's linked to another move. """
        move_create_proc = self.env['stock.move']
        move_to_confirm = self.env['stock.move']
        move_waiting = self.env['stock.move']

        to_assign = {}
        self.set_default_price_unit_from_product()
        
        self.push_price()
        for move in self:
            # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_waiting |= move
            # if the move is split and some of the ancestor was preceeded, then it's waiting as well
            else:
                inner_move = move.split_from
                while inner_move:
                    if inner_move.move_orig_ids:
                        move_waiting |= move
                        break
                    inner_move = inner_move.split_from
                else:
                    if move.procure_method == 'make_to_order':
                        move_create_proc |= move
                    else:
                        move_to_confirm |= move

            if not move.picking_id and move.picking_type_id:
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = self.env['stock.move']
                to_assign[key] |= move

        # create procurements for make to order moves
        procurements = self.env['procurement.order']
        for move in move_create_proc:
            procurements |= procurements.create(move._prepare_procurement_from_move())
        if procurements:
            procurements.run()

        move_to_confirm.write({'state': 'confirmed'})
        (move_waiting | move_create_proc).write({'state': 'waiting'})

        # assign picking in batch for all confirmed move that share the same details
        for key, moves in to_assign.items():
            moves.assign_picking()
        self._push_apply()
        return self

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    productCode = fields.Char('HSN Code')
    
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        self.productCode = self.product_id.hs_code
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)
        self.update(vals)

        return result
    
    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {}
        account = self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id
        if not account:
            raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                (self.product_id.name, self.product_id.id, self.product_id.categ_id.name))

        fpos = self.order_id.fiscal_position_id or self.order_id.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account)

        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'discount': self.discount,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'layout_category_id': self.layout_category_id and self.layout_category_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
            'account_analytic_id': self.order_id.project_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'HsnCode': self.product_id.hs_code,
        }
        return res



