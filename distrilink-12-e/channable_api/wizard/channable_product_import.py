# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################


import io
import base64
from urllib.request import urlopen
import requests
from PIL import Image

from odoo import models, fields, api, _
from odoo.tools import pycompat
from odoo.exceptions import UserError


class ChannableProductImport(models.TransientModel):
    _name = 'channable.product.import'
    _description = 'Channable Product Import'
    _rec_name = 'channable_file_name'

    channable_product_file = fields.Binary('Product File')
    channable_file_name = fields.Char('File Name', size=64)
    delimiter = fields.Char('Delimiter', size=1, default=';')

    def read_csv(self, file_data):
        inputx = io.BytesIO()
        inputx.write(base64.decodestring(file_data))
        csv_iterator = pycompat.csv_reader(
            io.BytesIO(inputx.getvalue()),
            delimiter=self.delimiter)
        return (
            row for row in csv_iterator
            if any(x for x in row if x.strip())
        )

    def processChannableProductPrice(self, data, product_variant_id):
        channablePriceObj = self.env['channable.product.price']
        channable_ids = []
        channablePrice = channablePriceObj.search([
            ('product_id', '=', product_variant_id.id)
        ])
        if not channablePrice:
            price = data['Cost']
            channablePrice = channablePriceObj.create({
                'name': data['Product Name'],
                'product_id': product_variant_id.id,
                'channable_price_amount': price
            })
        channable_ids.append(channablePrice.id)
        # return channablePrice
        return channable_ids

    def processChannableVendor(self, data, product_variant_id):
        resPartnerObj = self.env['res.partner']
        channableVendorObj = self.env['product.supplierinfo']
        resPartner = resPartnerObj.search([
            ('name', '=', data['Vendor'])
        ])
        if not resPartner:
            resPartner = resPartnerObj.create({
                'name': data['Vendor'],
                'supplier': True
            })
        channableVendor = channableVendorObj.search([
            ('name', '=', resPartner.id),
            ('product_id', '=', product_variant_id.id)
        ])
        channableOldVendor = channableVendorObj.search([
            ('product_id', '=', product_variant_id.id),
            ('id', 'not in', channableVendor.ids)
        ])
        if channableOldVendor:
            for old in channableOldVendor:
                old.unlink()
        if not channableVendor:
            purchasePrice = data['Cost']
            channableVendor = channableVendorObj.create({
                'name': resPartner.id,
                'product_id': product_variant_id.id,
                'min_qty': 1,
                'price': purchasePrice
            })
        return channableVendor

    def processProductAttributes(self, attrsData, product_template):
        attrKeysObj = self.env['product.attribute']
        attribtesObj = self.env['product.attribute.value']
        attrlinesObj = self.env['product.template.attribute.line']
        attrs = {'Color Code': attrsData['Color Code'], 'Item Code': attrsData['Item Code'], 'Size': attrsData['Size']}
        for key, val in attrs.items():
            if key and val:
                attrKeys = attrKeysObj.search([
                    ('name', 'in', [key])])
                if not attrKeys:
                    attrKeys = attrKeysObj.create({'name': key,
                                                   'create_variant': 'no_variant'})
                attribtes = attribtesObj.search([
                    ('name', 'in', [val]),
                    ('attribute_id', 'in', attrKeys.ids)])
                if not attribtes:
                    attribtes = attribtesObj.create({'attribute_id': attrKeys.id,
                                                     'name': val})

                product_attr_lines = attrlinesObj.search([
                    ('attribute_id', 'in', attrKeys.ids),
                    ('product_tmpl_id', '=', product_template.id)])

                if not product_attr_lines:
                    product_attr_lines = attrlinesObj.create({
                        'product_tmpl_id': product_template.id,
                        'attribute_id': attribtes.attribute_id.id,
                        'value_ids': [(6, False, attribtes.ids)]
                    })
                else:
                    product_attr_lines.write(
                        {'value_ids': [(4, attribtes.id)]})


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
                # ('name', '=', data['Name:en']),
            ])
            # link = data['Vendors/Product Image']
            # r = requests.get(link)
            # Image.open(io.BytesIO(r.content))
            # profile_image = base64.encodestring(urlopen(link).read())
            if not productTemplate:
                productTemplate = productTemplateObj.create({
                    'name': data.get('Variant Name') or data.get('Product Name'),
                    # 'image_medium': profile_image,
                    'type': 'product',
                    'channable_brand': data.get('Brand'),
                    'list_price': data.get('Sales Price') or 0.0,
                    'default_code': data.get('SKU'),
                    'barcode': data.get('Barcode'),
                    'standard_price': data.get('Cost') or 0.0,
                    'is_fba': True if data.get('FBA') == 'yes' else False,
                    'is_fbb': True if data.get('FBB') == 'yes' else False
                })
            self.processProductAttributes(data, productTemplate)
            vendor = self.processChannableVendor(data, productTemplate.product_variant_id)
            # productPrice = self.processChannableProductPrice(data, productTemplate.product_variant_id)
            productTemplate.write({
                'channable_vendor_ids': vendor.id,
                'seller_ids': [(6, 0, vendor.ids)]
                # 'channable_product_price': [(6, 0, productPrice)]
            })
        return productTemplate

