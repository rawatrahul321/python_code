# -*- coding: utf-8 -*-

from odoo.addons import decimal_precision as dp
from odoo import models, fields, api, _


class multi_uom(models.Model):
    _name = 'product.multi.uom.price'
    _description = 'Product multiple uom price'

    pro_id = fields.Many2one('product.product', _('Product'), ondelete='set null', readonly=True)
    product_id = fields.Many2one('product.template', _('Product Template'), ondelete='set null', readonly=True)
    category_id = fields.Many2one('uom.category', _('Category'), ondelete='set null', readonly=True)
    uom_id = fields.Many2one('uom.uom', string=_("Unit of Measure"), required=True)
    price = fields.Float(_('Price'), required=True, digits=dp.get_precision('Product Price'))
    barcode = fields.Char(string="Barcode", required=True)

    # _sql_constraints = [
    #     ('product_multi_uom_price_barcode_uniq', 'UNIQUE (barcode)', _("A barcode can only be assigned to one product UOM !")),
    # ]

    @api.constrains('barcode')
    def _check_barcode_unique(self):
        for rec in self:
            barcode = rec.barcode
            data = self.env['product.multi.uom.price'].search([('barcode', '=', barcode)])
            if 1 < len(data):
                raise ValueError(_('Error ! Barcode must be unique.'))

    @api.model
    def create(self, vals):
        res = super(multi_uom, self).create(vals)
        if res and not res.product_id:
            res.product_id = res.pro_id.product_tmpl_id.id
        return res

    # EHDLF Categoría del producto
    @api.onchange('product_id')
    def categorydefault(self):
        if not (self.product_id):
            self.category_id = False
        else:
            self.category_id = self.product_id.uom_id.category_id.id

    # EHDLF UOM's de la categoria
    @api.onchange('product_id')
    def categorysuom(self):
        if not self.product_id:
            return
        # EHDLF misma categoría y diferente base
        domain = {'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id), '!',
                             ('id', '=', self.product_id.uom_id.id)]}
        return {'domain': domain}

    # EHDLF Convinación Producto-UOM debe ser única
    _sql_constraints = [
        ('product_multi_uom_price_uniq',
         'UNIQUE (product_id,uom_id)',
         _('Product-UOM must be unique and there are duplicates!'))]
