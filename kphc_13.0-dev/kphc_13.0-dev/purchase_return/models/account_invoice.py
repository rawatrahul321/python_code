# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import odoo.addons.decimal_precision as dp



class AccountInvoice(models.Model):
    _inherit = 'account.move'


    apply_discount = fields.Boolean('Apply Discount')

    return_id = fields.Many2one('return.order', string='Add Return Order',
                                help='Encoding help. When selected, the associated return order lines are added '
                                     'to the vendor bill. Several RO can be selected.')


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"
    _order = 'id asc'

    return_line_id = fields.Many2one('return.order.line', 'Return Order Line', ondelete='set null',
                                     index=True, readonly=True)
    return_id = fields.Many2one('return.order', related='return_line_id.order_id', string='Return Order',
                                store=False, readonly=True, related_sudo=False,
                                help='Associated Return Order. '
                                     'Filled in automatically when a RO is chosen on the vendor bill.')


    discount_type = fields.Selection([
        ('fixed', 'Amount'),
        ('bonus', 'Bonus'),
        ('percent', 'Percent')
    ], string="Discount Type", )

    price_subtotal = fields.Float(string='Subtotal',compute="get_new_sub_total")

    def get_new_sub_total(self , ):
            for rec in self:
                rec.price_subtotal = 0.0
                if rec.credit:
                    rec.price_subtotal = rec.credit






    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        price_subtotal *= sign
        if currency and currency != company.currency_id:
            # Multi-currencies.
            balance = currency._convert(price_subtotal, company.currency_id, company, date)
            return {
                'amount_currency': price_subtotal,
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
            }
        else:
            if  not self.move_id.return_id:
                return {
                    'amount_currency': 0.0,
                    'debit': price_subtotal > 0.0 and price_subtotal or 0.0,
                    'credit': price_subtotal < 0.0 and -price_subtotal or 0.0,
                }
            else:

                self._compute_amount()
                print(self.price_subtotal * -1)
                self.price_subtotal = (self.price_subtotal * -1)
                return {
                    'amount_currency': 0.0,
                    'debit': self.price_subtotal > 0.0 and self.price_subtotal or 0.0,
                    'credit': self.price_subtotal < 0.0 and -self.price_subtotal or 0.0,
                    'price_subtotal': self.price_subtotal,
                }

    @api.model
    def _get_fields_onchange_balance_model(self, quantity, discount, balance, move_type, currency, taxes, price_subtotal):
        ''' This method is used to recompute the values of 'quantity', 'discount', 'price_unit' due to a change made
        in some accounting fields such as 'balance'.

        This method is a bit complex as we need to handle some special cases.
        For example, setting a positive balance with a 100% discount.

        :param quantity:        The current quantity.
        :param discount:        The current discount.
        :param balance:         The new balance.
        :param move_type:       The type of the move.
        :param currency:        The currency.
        :param taxes:           The applied taxes.
        :param price_subtotal:  The price_subtotal.
        :return:                A dictionary containing 'quantity', 'discount', 'price_unit'.
        '''
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        balance *= sign

        # Avoid rounding issue when dealing with price included taxes. For example, when the price_unit is 2300.0 and
        # a 5.5% price included tax is applied on it, a balance of 2300.0 / 1.055 = 2180.094 ~ 2180.09 is computed.
        # However, when triggering the inverse, 2180.09 + (2180.09 * 0.055) = 2180.09 + 119.90 = 2299.99 is computed.
        # To avoid that, set the price_subtotal at the balance if the difference between them looks like a rounding
        # issue.
        if currency.is_zero(balance - price_subtotal):
            return {}

        taxes = taxes.flatten_taxes_hierarchy()
        if taxes and any(tax.price_include for tax in taxes):
            # Inverse taxes. E.g:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 110           | 10% incl, 5%  |                   | 100               | 115
            # 10            |               | 10% incl          | 10                | 10
            # 5             |               | 5%                | 5                 | 5
            #
            # When setting the balance to -200, the expected result is:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 220           | 10% incl, 5%  |                   | 200               | 230
            # 20            |               | 10% incl          | 20                | 20
            # 10            |               | 5%                | 10                | 10
            taxes_res = taxes._origin.compute_all(balance, currency=currency, handle_price_include=False)
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])
                if tax.price_include:
                    balance += tax_res['amount']

        discount_factor = 1 - (discount / 100.0)
        if balance and discount_factor:
            # discount != 100%
            vals = {
                'quantity': quantity or 1.0,
                # 'price_unit': balance / discount_factor / (quantity or 1.0),
            }
        elif balance and not discount_factor:
            # discount == 100%
            vals = {
                'quantity': quantity or 1.0,
                'discount': 0.0,
                # 'price_unit': balance / (quantity or 1.0),
            }
        else:
            vals = {}
        return vals



    @api.model
    @api.depends('price_unit', 'discount', 'discount_type', 'tax_ids', 'quantity',
                 'product_id', 'move_id.partner_id', 'move_id.currency_id', 'move_id.company_id',
                 'move_id.date_invoice')
    def _compute_price(self):
        for rec in self:
            print(rec.price_avg,rec.name, rec.discount_type)
            currency = rec.move_id and rec.move_id.currency_id or None
            for line in self:
                quantity = line.quantity
                price = line.price_unit * quantity
                if line.discount:
                    if line.discount_type == 'fixed':
                        price = price - line.discount

                    if line.discount_type == 'percent':

                        price = price - (line.discount*price/100.0)
                taxes = False
                if line.tax_ids:
                    taxes = line.tax_ids.compute_all(price, currency, quantity, product=line.product_id,
                                                                  partner=line.move_id.partner_id)
                line.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else  price
                if line.move_id.currency_id and line.move_id.company_id and line.move_id.currency_id != line.move_id.company_id.currency_id:
                    price_subtotal_signed = line.move_id.currency_id.with_context(
                        date=line.move_id.date_invoice).compute(
                        price_subtotal_signed, line.move_id.company_id.currency_id)
                sign = line.move_id.type in ['in_refund', 'out_refund'] and -1 or 1
                line.price_subtotal_signed = price_subtotal_signed * sign

    @api.onchange('quantity', 'price_unit', 'tax_ids', 'discount', 'discount_type')
    def _compute_amount(self):
        # print('gggg')

        for line in self:
            quantity = line.quantity or 1.0
            newprice = line.price_unit * quantity
            line.price_subtotal = newprice
            price = line.price_unit * quantity
            if line.discount:
                if line.discount_type == 'fixed':
                    newprice = newprice - line.discount
                elif line.discount_type == 'percent':
                    newprice = newprice - (line.discount*newprice/100.0)
                elif line.discount_type == 'bonus':
                    newprice = newprice
            taxes = line.tax_ids.compute_all(
                price, line.move_id.currency_id, quantity, product=line.product_id, partner=line.move_id.partner_id)
            print("new_price ==> ",newprice)
            line.update({
                'price_subtotal': newprice,
                # 'total': price - newprice
            })

