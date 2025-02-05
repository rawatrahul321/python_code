# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class GSTConfigure(models.Model):
    _inherit = "res.company"

    gst_configuration = fields.Boolean(string='GST Configuration')

    @api.model
    def create(self,vals):
        res = super(GSTConfigure,self).create(vals)
        products = self.env['product.template']
        tax_ids = self.env['account.tax'].search([
                    ('type_tax_use','=','purchase'),
                    ('company_id','=',res.id)])
        if res.gst_configuration:
            products.search([]).write({
                'supplier_taxes_id': [(4, tax_id.id) for tax_id in tax_ids]
            })
        return res

    @api.multi
    def write(self,vals):
        products = self.env['product.template']
        if vals.get('gst_configuration'):
            tax_ids = self.env['account.tax'].search([
                    ('type_tax_use','=','purchase'),
                    ('company_id','=',self.id)])
            products.search([]).write({
                'supplier_taxes_id': [(4, tax_id.id) for tax_id in tax_ids]
            })
        elif not vals.get('gst_configuration', True):
            products = self.env['product.template'].search([])
            tax_ids = self.env['account.tax'].search([
                ('type_tax_use','=','purchase'),
                ('company_id','=',self.id)])
            for rec in products:
                rec.write({
                        'supplier_taxes_id':
                            [(3, tax_id.id) for tax_id in tax_ids]
                        })
        res = super(GSTConfigure,self).write(vals)
        return res


class AddVendorTaxesInProduct(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        res = super(AddVendorTaxesInProduct, self).create(vals)
        company = self.env['res.company'].search([('gst_configuration',
            '=',True)])
        for cmpn in company:
            if cmpn:
                tax_ids = self.env['account.tax'].search([
                    ('type_tax_use','=','purchase'),
                    ('company_id','=',cmpn.id)])
                for record in res:
                    record.write({
                            'supplier_taxes_id':
                                [(4, tax_id.id) for tax_id in tax_ids]
                    })
        return res