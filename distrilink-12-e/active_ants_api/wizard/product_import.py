# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models, _
from odoo.exceptions import UserError

class ChannableProductImport(models.TransientModel):
    _inherit = 'channable.product.import'

    def import_channable_products(self):
        file_datas = self.read_csv(self.channable_product_file)
        rows = [rows for rows in file_datas]
        product_dict = []
        for row in rows[1:]:
            product_dict.append(dict(zip(rows[0], row)))
        for data in product_dict:
            if not 'Barcode' in data:
                raise UserError(_("Make Sure File Delimiter is Correct."))
            productTemplateObj = self.env['product.template']
            productTemplate = productTemplateObj.search([
                ('barcode', '=', data.get('Barcode')),
            ])
            if not productTemplate:
                productTemplate = productTemplateObj.create({
                    'name': data.get('Variant Name') or data.get('Product Name'),
                    'type': 'product',
                    'channable_brand': data.get('Brand'),
                    'list_price': data.get('Sales Price') or 0.0,
                    'default_code': data.get('SKU'),
                    'barcode': data.get('Barcode'),
                    'standard_price': data.get('Cost') or 0.0,
                    'is_fba': True if data.get('FBA') == 'yes' else False,
                    'is_fbb': True if data.get('FBB') == 'yes' else False,
                    'is_active_ants': True if data.get('ANTS') == 'yes' else False,
                })
            self.processProductAttributes(data, productTemplate)
            vendor = self.processChannableVendor(data, productTemplate.product_variant_id)
            productTemplate.write({
                'channable_vendor_ids': vendor.id,
                'seller_ids': [(6, 0, vendor.ids)]
            })
        return productTemplate
