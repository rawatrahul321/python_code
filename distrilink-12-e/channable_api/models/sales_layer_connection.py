# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging

from odoo import api, fields, models, _
from odoo.addons.channable_api.models.authorization import AuthorizeSaleslayer
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class SaleslayerConnection(models.Model):
    _name = 'saleslayer.connection'
    _description = 'Saleslayer Connection'

    name = fields.Char('Name')
    code = fields.Char('Code')
    private_key = fields.Char('Private Key')
    url = fields.Char('URL', default='https://api.saleslayer.com')

    def test_saleslayer_connection(self):
        res = AuthorizeSaleslayer(self.url, self.code, self.private_key).get_request()
        if 'error' in res:
            raise UserError(_("Make Sure Saleslayer Configuration Details are Valid."))
        raise UserError(_('Connection Test Succeeded! Everything seems properly set up!'))

    def processProductVendor(self, vendor, cost, product_variant_id):
        resPartnerObj = self.env['res.partner']
        channableVendorObj = self.env['product.supplierinfo']
        resPartner = resPartnerObj.search([
            ('name', '=', vendor)
        ])
        if not resPartner:
            resPartner = resPartnerObj.create({
                'name': vendor or '',
                'supplier': True
            })
        channableVendor = channableVendorObj.search([
            ('name', '=', resPartner.id),
            ('product_id', '=', product_variant_id)
        ])
        channableOldVendor = channableVendorObj.search([
            ('product_id', '=', product_variant_id),
            ('id', 'not in', channableVendor.ids)
        ])
        if channableOldVendor:
            for old in channableOldVendor:
                old.unlink()
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
                    product_attr_lines.write(
                        {'value_ids': [(4, attribtes.id)]})

    # def syncProducts(self):
    #     conns = self.search([])
    #     productCount = 0
    #     for con in conns:
    #         result = AuthorizeSaleslayer(con.url, con.code, con.private_key).get_request()
    #         print ('result...........', result)
    #         productTemplateObj = self.env['product.template']
    #         if 'data' in result:
    #             products = result.get('data').get('products')
    #             variants_dict = {}
    #             for product in products:
    #                 variants_dict[product[1]] = []
    #             if result.get('data').get('odoo_products'):
    #                 for res in result.get('data').get('odoo_products'):
    #                     print ('res..........', res)
    #                     variants_dict[res[2]].append(res)
    #                 for product in products:
    #                     print ('product.........', product)
    #                     variants = variants_dict.get(product[1])
    #                     for variant in variants:
    #                         print ('variant.........', variant)
    #                         if variant and variant[2] == product[1]:
    #                             productTemplate = productTemplateObj.search([
    #                                 ('barcode', '=', variant[6]),
    #                             ])
    #                             cost = variant[10] or product[10]
    #                             color_code = variant[8] or product[8]
    #                             size = variant[7] or product[11]
    #                             if not productTemplate:
    #                                 productTemplate = productTemplateObj.create({
    #                                     'name': variant[9] or product[4],
    #                                     'type': 'product',
    #                                     'channable_brand': product[5] or variant[4],
    #                                     'default_code': variant[9],
    #                                     'barcode': variant[3],
    #                                 })
    #                             self.processProductAttributes(color_code, product[5], size, productTemplate.id)
    #                             vendor = self.processProductVendor(product[9], cost, productTemplate.product_variant_id.id)
    #                             productTemplate.write({
    #                                 'channable_vendor_ids': vendor.id,
    #                                 'seller_ids': [(6, 0, vendor.ids)],
    #                                 'list_price': variant[6] or product[8] or 0.0,
    #                                 'standard_price': cost,
    #                                 'is_fba': True if variant[11] == 'yes' else False,
    #                                 'is_fbb': True if variant[10] == 'yes' else False
    #                             })
    #                             print ('productTemplate..........', productTemplate)
    #     cron = self.env.ref('channable_api.ir_cron_get_saleslayer_products')
    #     message = ['%s Products are synced successfully' % (productCount)]
    #     self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def syncProducts(self):
        conns = self.search([])
        productCount = 0
        for con in conns:
            result = AuthorizeSaleslayer(con.url, con.code, con.private_key).get_request()
            productTemplateObj = self.env['product.template']
            if 'data' in result:
                if result.get('data').get('odoo_products'):
                    for product in result.get('data').get('odoo_products'):
                        productTemplate = productTemplateObj.search([
                            '|', ('active', '=', False), ('active', '=', True),
                            ('barcode', '=', product[6]),
                        ])
                        productProduct = self.env['product.product'].search([
                            '|', ('active', '=', False), ('active', '=', True),
                            ('barcode', '=', product[6]),
                        ])
                        logger.info('barcode, productProduct, productTemplate....................%s, %s, %s'%(product[6], productProduct, productTemplate))
                        cost = product[10]
                        color_code = product[8]
                        size = product[7]
                        if not productTemplate and not productProduct:
                            productTemplate = productTemplateObj.create({
                                'name': product[9],
                                'type': 'product',
                                'channable_brand': product[4],
                                'default_code': product[3],
                                'barcode': product[6],
                            })
                        self.processProductAttributes(color_code, product[15], size, productTemplate.id)
                        vendor = self.processProductVendor(product[14], cost, productTemplate.product_variant_id.id)
                        productTemplate.write({
                            'channable_vendor_ids': vendor.id,
                            'seller_ids': [(6, 0, vendor.ids)],
                            'list_price': product[5] or 0.0,
                            'standard_price': cost,
                            'is_fba': True if product[11] == 'yes' else False,
                            'is_fbb': True if product[12] == 'yes' else False
                        })
                        print ('productTemplate..........', productTemplate)
        cron = self.env.ref('channable_api.ir_cron_get_saleslayer_products')
        message = ['%s Products are synced successfully' % (productCount)]
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
