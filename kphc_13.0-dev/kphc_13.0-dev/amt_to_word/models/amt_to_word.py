# -*- coding: utf-8 -*-

from num2words import num2words

from os import listdir
from os.path import isfile, join
from odoo import fields, models, api, exceptions
from odoo.tools.translate import _
from datetime import datetime
from datetime import date, timedelta


def get_amount_in_words_module(amount, currency_unit, currency_subunit):
    pre = format(amount, '.3f')
    text = ''
    entire_num = int((str(pre).split('.'))[0])
    decimal_num = int((str(pre).split('.'))[1])
    text += num2words(entire_num, lang='en').capitalize()
    text += ' ' + str(currency_unit) + ' and '
    text += num2words(decimal_num, lang='en').capitalize()
    text += ' ' + str(currency_subunit)
    return text


# class PurchaseOrderLine(models.Model):
#     _inherit = 'purchase.order.line'
#
#     qty_available = fields.Float(
#         related='product_id.qty_available',
#         readonly=True,
#     )


# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     # qty_available = fields.Float(related='product_id.qty_available',readonly=True)
#     qty_available = fields.Float(readonly=True)


# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'
#
#     @api.depends('order_line.product_qty')
#     def get_the_product_quantity(self):
#         for rec in self:
#             total_qty = 0.0
#             for lines in rec.order_line:
#                 total_qty += lines.product_qty
#             rec.total_product_qty = total_qty
#
#     currency_id = fields.Many2one('res.currency', string='Company Currency')
#     amt_to_word = fields.Text(string="Amount In Word", compute='onchange_total_amount_get_words')
#     total_product_qty = fields.Float(string="Total Product Qty", compute="get_the_product_quantity")
#
#     @api.depends('amount_total')
#     def onchange_total_amount_get_words(self):
#         for rec in self:
#             words = get_amount_in_words_module(rec.amount_total, rec.currency_id.currency_unit_label, rec.currency_id.currency_subunit_label)
#             rec.amt_to_word = words


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     @api.depends('order_line')
#     def get_the_product_uom_quantity(self):
#         for rec in self:
#             total_qty = 0.0
#             for lines in rec.order_line:
#                 total_qty += lines.product_uom_qty
#             rec.total_product_uom_qty = total_qty
#
#     currency_id = fields.Many2one('res.currency', string='Company Currency')
#     amt_to_word = fields.Text(string="Amount In Word", compute='onchange_amount_get_word')
#     total_product_uom_qty = fields.Float(string="Total Product Qty", compute="get_the_product_uom_quantity")
#
#     @api.depends('amount_total')
#     def onchange_amount_get_word(self):
#         for rec in self:
#             words = get_amount_in_words_module(rec.amount_total, rec.currency_id.currency_unit_label, rec.currency_id.currency_subunit_label)
#             rec.amt_to_word = words


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    # @api.depends('invoice_line_ids')
    # def get_the_product_qty(self):
    #     total_qty = 0.0
    #     for inv_id in self:
    #         for lines in inv_id.invoice_line_ids:
    #             total_qty += lines.quantity
    #         inv_id.total_product_qty = total_qty

    # currency_unit_id = fields.Many2one('res.currency', string='Company Currency')
    amt_to_word = fields.Text(string="Amount In Word", compute='onchange_amt_get_words')

    # total_product_qty = fields.Float(string="Total Product Qty", compute="get_the_product_qty")

    @api.depends('amount_total')
    def onchange_amt_get_words(self):
        for rec in self:
            words = get_amount_in_words_module(rec.amount_total, rec.currency_id.currency_unit_label,
                                               rec.currency_id.currency_subunit_label)
            print("\n 11 11 11 11 11 11 11 11 11  words = ", words)
            rec.amt_to_word = words

# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
#
#     @api.depends('move_ids_without_package')
#     def _get_total_product_qty(self):
#         total_qty_demand = 0.0
#         total_qty_done = 0.0
#         for lines in self.move_ids_without_package:
#             total_qty_demand += lines.product_uom_qty
#             total_qty_done += lines.quantity_done
#         self.total_product_qty_demand = total_qty_demand
#         self.total_product_qty_done = total_qty_done
#
#     total_product_qty_demand = fields.Float(string="Total Initial Demand", compute="_get_total_product_qty")
#     total_product_qty_done = fields.Float(string="Total Qty Done", compute="_get_total_product_qty")
