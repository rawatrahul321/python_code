# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Devintelle Software Solutions (<http://devintelle.com>).
#
##############################################################################
from odoo import models, fields, api, _
from operator import itemgetter


class ResPartner(models.Model):
    """ Add gst Number """
    _inherit = 'res.partner'
    # _description = 'Add gst Number'

    partner_gst_number = fields.Char('GST Number')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_cgst_tax_rate_amount(self):
        res = []
        for line in self.tax_line_ids:
            if 'CGST' in line.name:
                perc = int(list(filter(str.isdigit,str(line.name)))[0])
                sign = "%s %d%%" % ("", perc)
                res.append ({
                    'name': sign,
                    'amount': line.amount,
                })
        return res

    @api.multi
    def _get_sgst_tax_rate_amount(self):
        res = []
        for line in self.tax_line_ids:
            if 'SGST' in line.name:
                perc = int(list(filter(str.isdigit,str(line.name)))[0])
                sign = "%s %d%%" % ("", perc)
                res.append ({
                    'name': sign,
                    'amount': line.amount,
                })
        return res

    @api.multi
    def _get_igst_tax_rate_amount(self):
        res = []
        for line in self.tax_line_ids:
            if 'IGST' in line.name:
                perc = int(list(filter(str.isdigit,str(line.name)))[0])
                sign = "%s %d%%" % ("", perc)
                res.append ({
                    'name': sign,
                    'amount': line.amount,
                })
        return res

    @api.multi
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = self.currency_id.amount_to_text(amount)
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words


class ProductProduct(models.Model):
    _inherit = 'product.product'

    hsn_code = fields.Char('HSN Code')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hsn_code = fields.Char('HSN Code')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: