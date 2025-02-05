# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging
import datetime

from odoo import api, fields, models, _
from odoo.addons.sales_layer_api.models.authorization import AuthorizeSaleslayer
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class SaleslayerConnection(models.Model):
    _name = 'saleslayer.connection'
    _description = 'Saleslayer Connection'

    name = fields.Char('Name')
    code = fields.Char('Code')
    private_key = fields.Char('Private Key')
    url = fields.Char('URL', default='https://api.saleslayer.com')
    start_index = fields.Integer('Start Index', default=0)
    end_index = fields.Integer('End Index', default=500)
    gapping_index = fields.Integer('Gapping Index', default=500)
    last_modified_hours = fields.Integer('Last Modified Hours', default=25)

    def test_saleslayer_connection(self):
        res = AuthorizeSaleslayer(self.url, self.code, self.private_key, self.last_modified_hours).get_request()
        if 'error' in res:
            raise UserError(_("Make Sure Saleslayer Configuration Details are Valid."))
        raise UserError(_('Connection Test Succeeded! Everything seems properly set up!'))

    def processProductVendor(self, vendor, cost, product_variant_id):
        resPartnerObj = self.env['res.partner']
        channableVendorObj = self.env['product.supplierinfo']
        resPartner = resPartnerObj.search([
            ('name', '=', vendor), ('supplier', '=', True)
        ])
        if not resPartner:
            resPartner = resPartnerObj.create({
                'name': vendor or '',
                'supplier': True
            })
        channableVendor = channableVendorObj.search([
            ('name', '=', resPartner.id),
            ('product_id', '=', product_variant_id)
        ], limit=1)
        channableOldVendor = channableVendorObj.search([
            ('product_id', '=', product_variant_id),
            ('id', 'not in', channableVendor.ids)
        ])
        if channableOldVendor:
            for old in channableOldVendor:
                old.unlink()
        if channableVendor and channableVendor.price != cost:
            channableVendor.write({'price': cost})
        if not channableVendor:
            purchasePrice = cost
            channableVendor = channableVendorObj.create({
                'name': resPartner.id,
                'product_id': product_variant_id,
                'min_qty': 1,
                'price': purchasePrice
            })
        return channableVendor

    def processProductAttributes(self, color_code, item_code, size, product_template_id):
        attrKeysObj = self.env['product.attribute']
        attribtesObj = self.env['product.attribute.value']
        attrlinesObj = self.env['product.template.attribute.line']
        attrs = {'Color Code': color_code, 'Item Code': item_code, 'Size': size}
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
                    ('product_tmpl_id', '=', product_template_id)])

                if not product_attr_lines:
                    product_attr_lines = attrlinesObj.create({
                        'product_tmpl_id': product_template_id,
                        'attribute_id': attribtes.attribute_id.id,
                        'value_ids': [(6, False, attribtes.ids)]
                    })
                else:
                    # product_attr_lines.write(
                    #     {'value_ids': [(4, attribtes.id)]})
                    product_attr_lines.write(
                        {'value_ids': [(6, False, attribtes.ids)]})

    def chunkProducts(self):
        final_data = []
        result = AuthorizeSaleslayer(self.url, self.code, self.private_key, self.last_modified_hours).get_request()
        # self.env['audit.log'].put_audit_log(
        #         'Sync Product from Saleslayer to Odoo', 'Success', result, '')
        if 'data' in result:
            odoo_products = result.get('data').get('odoo_products')
            if odoo_products:
                if self.start_index >= len(odoo_products):
                    self.start_index = 0
                    self.end_index = self.gapping_index
                if self.end_index > len(odoo_products):
                    self.end_index = len(odoo_products)
                final_data.extend(odoo_products[self.start_index:self.end_index])
        return final_data

    def last_modified_date(self):
        return datetime.datetime.now() - datetime.timedelta(hours = self.last_modified_hours)

    def syncProducts(self):
        cron = self.env.ref('sales_layer_api.ir_cron_sync_saleslayer_products')
        conns = self.search([])
        products = []
        not_updated_products = []
        for con in conns:
            productTemplateObj = self.env['product.template']
            # Comment for run cron job only once with last modification date
            # product_status = False
            # for product in con.chunkProducts():
            result = AuthorizeSaleslayer(con.url, con.code, con.private_key, con.last_modified_hours).get_request()
            self.env['audit.log'].put_audit_log(cron.name, 'Success', result, '')
            if 'data' in result:
                odoo_products = result.get('data').get('odoo_products')
                if odoo_products:
                    for product in odoo_products:
                        if len(product) > 2 and datetime.datetime.strptime(product[17], '%d/%m/%Y %H:%M:%S') >= con.last_modified_date():
                            # if len(product) > 2:
                            productTemplate = productTemplateObj.search([
                                '|', ('active', '=', False), ('active', '=', True),
                                ('barcode', '=', product[6]),
                            ])
                            productProduct = self.env['product.product'].search([
                                '|', ('active', '=', False), ('active', '=', True),
                                ('barcode', '=', product[6]),
                            ])
                            cost = product[10]
                            color_code = product[8]
                            size = product[7]
                            if not productTemplate and not productProduct:
                                productTemplate = productTemplateObj.create({
                                    'name': product[9],
                                    'type': 'product',
                                    'barcode': product[6]
                                })
                            if productTemplate:
                                self.processProductAttributes(color_code, product[15], size, productTemplate.id)
                                vendor = self.processProductVendor(product[14], cost, productTemplate.product_variant_id.id)
                                if productTemplate.default_code == productTemplate.marchant_product_no or productTemplate.marchant_product_no != product[3]:
                                    productTemplate.marchant_product_no = product[3]
                                if productTemplate.default_code == productTemplate.channable_product_id or productTemplate.channable_product_id != product[3]:
                                    productTemplate.channable_product_id = product[3]
                                productTemplate.write({
                                    'name': product[9],
                                    'default_code': product[3],
                                    'list_price': product[5] or 0.0,
                                    'standard_price': cost,
                                    'channable_brand': product[4],
                                    'is_fba': True if product[11] == 'yes' else False,
                                    'is_fbb': True if product[12] == 'yes' else False,
                                    'is_active_ants': True if product[13] == 'yes' else False,
                                    'channable_vendor_ids': vendor.id,
                                    'seller_ids': [(6, 0, vendor.ids)]
                                })
                                # product_status = True
                                products.append(productTemplate.barcode)
                            else:
                                not_updated_products.append(product[6])
                # if product_status:
                #     con.start_index = con.end_index
                #     con.end_index += con.gapping_index

        message = ['%s Products are synced successfully. \n\n Products are not Updated %s' % (products, not_updated_products)]
        self.env['audit.log'].put_audit_log(cron.name, 'Success', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
