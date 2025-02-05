# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging
import datetime

from odoo import models, fields, api
from odoo.addons.sales_layer_api.models.authorization import AuthorizeSaleslayer

logger = logging.getLogger(__name__)


class SaleslayerConnection(models.Model):
    _inherit = 'saleslayer.connection'

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
            logger.info('result.......................%s'%result)
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
                                if productTemplate.default_code == productTemplate.marchant_product_no and productTemplate.marchant_product_no != product[3]:
                                    productTemplate.marchant_product_no = product[3]
                                if productTemplate.default_code == productTemplate.channable_product_id and productTemplate.channable_product_id != product[3]:
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
                                    'seller_ids': [(6, 0, vendor.ids)],
                                    'is_kentucky_active_ants': True if product[16] == 'yes' else False,
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
