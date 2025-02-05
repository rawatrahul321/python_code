# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import csv
import os
import datetime
import logging
import tempfile
import base64
import hashlib
import io
import re
import pytz

from odoo import api, fields, models, _
from odoo.addons.channable_api.models.authorization import AuthorizeFTP
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)

class ftpConnection(models.Model):
    _inherit = 'ftp.connection'


    def exportOrders(self, product_ids):
        header = ['Odoo Order ID', 'Market Place Order Id', 'Customer Name', 'Street', 'Street 2', 'House Number',
            'House Number EXT', 'Address Supplement', 'City', 'Zip Code', 'Country Code', 'Order Date', 'Product Name',
            'Item Code', 'Color Code', 'Size', 'CostCenter', 'Quantity', 'EAN', 'SKU', 'MarketPlace', 'Customer Email',
            'Customer Phone', 'Company']

        sql = """SELECT count(pt.channable_vendor_ids), pt.channable_vendor_ids as vendor_id
                 FROM sale_order so
                 INNER JOIN sale_order_line sl
                 ON so.id=sl.order_id
                 INNER JOIN product_product pp
                 ON sl.product_id=pp.id
                 INNER JOIN product_template pt
                 ON pp.product_tmpl_id=pt.id
                 WHERE so.state='channable_order'
                 GROUP BY pt.channable_vendor_ids;"""
        self.env.cr.execute(sql)
        res_all = self.env.cr.dictfetchall()

        suppliers = []
        allPartners = []
        totalExportedFiles = 0
        conn = self.search([('location_type', '=', 'order_export')])
        for vendor in res_all:
            vendor_name = self.env['product.supplierinfo'].browse(vendor['vendor_id'])
            allPartners.append(vendor_name.name.id)
            suppliers.append(vendor_name.id)

        for partner in list(set(allPartners)):
            partnerName = self.env['res.partner'].browse(partner)
            now = fields.Datetime.now()
            timezone = pytz.timezone(self._context.get('tz') or 'Europe/Brussels' or 'UTC')
            filePrefix = 'Orders_%s_%s' % (partnerName.name, now.astimezone(timezone).strftime(DEFAULT_SERVER_DATETIME_FORMAT))
            csv_file = '%s.csv' % filePrefix
            file_fd, file_path = tempfile.mkstemp(suffix='.csv', prefix=filePrefix)

            products = self.env['product.product'].search(
                [('channable_vendor_ids', 'in', suppliers), ('id', 'in', product_ids)])
            sale_orders = self.env['sale.order'].search([
                ('state', '=', 'channable_order'), ('is_exported_to_ftp', '=', False)])
            sale_order_lines = self.env['sale.order.line'].search([
                ('product_id', 'in', products.ids), ('order_id', 'in', sale_orders.ids)])

            if sale_order_lines:
                with open(file_path, 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=header)
                    writer.writeheader()

                    for line in sale_order_lines:
                        MarketPlace_code = line.order_id.channable_channel_id.name[:3].upper()
                        if line.order_id.channable_channel_id and line.order_id.channable_channel_id.name == 'mirakl_kleertjes':
                            MarketPlace_code = line.order_id.channable_channel_id.name.split('_')[1][:3].upper()

                        # comment code because want to use another fields for housenumber and street
                        # streetHouseNumber = conn.getBarcode(
                        #     line.order_id.partner_shipping_id.street) if line.order_id.partner_shipping_id.street else ' '
                        # if streetHouseNumber:
                        #     street = line.order_id.partner_shipping_id.street.replace(
                        #         streetHouseNumber, '') if line.order_id.partner_shipping_id.street else ' '
                        # else:
                        #     street = line.order_id.partner_shipping_id.street if line.order_id.partner_shipping_id.street else ' '
                        # house_number = ''
                        # if not line.order_id.partner_shipping_id.house_number and streetHouseNumber:
                        #     house_number = streetHouseNumber
                        # else:
                        #     house_number = line.order_id.partner_shipping_id.house_number or ' '

                        if line.product_id.channable_vendor_ids.name == partnerName:
                            attrs = line.product_id.product_tmpl_id.attribute_line_ids
                            attrDict = {}
                            valName = ''
                            for attr in attrs:
                                name = [x.name for x in attr.value_ids]
                                if name:
                                   valName = ', '.join(name)
                                attrDict[attr.attribute_id.name] = valName

                            values = {
                                'Odoo Order ID': line.order_id.name or '',
                                'Market Place Order Id': line.order_id.channable_channel_id.channel_id or '',
                                'Customer Name': line.order_id.partner_shipping_id.name or line.order_id.partner_id.name,
                                'Street': line.order_id.partner_shipping_id.street if line.order_id.partner_shipping_id.street else ' ', # street,
                                'Street 2': line.order_id.partner_shipping_id.street2 or ' ',
                                'House Number': line.order_id.partner_shipping_id.house_number or ' ', # house_number,
                                'House Number EXT': line.order_id.partner_shipping_id.house_number_ext or ' ',
                                'Address Supplement': line.order_id.partner_shipping_id.Address_supplement or ' ',
                                'City': line.order_id.partner_shipping_id.city or ' ',
                                'Zip Code': line.order_id.partner_shipping_id.zip or ' ',
                                'Country Code': line.order_id.partner_shipping_id.country_id.code or ' ',
                                'Order Date': (line.order_id.channable_order_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                    if line.order_id.channable_order_date else False),
                                'Product Name': line.product_id.name,
                                'Item Code': attrDict['Item Code'] if 'Item Code' in attrDict else '',
                                'Color Code': attrDict['Color Code'] if 'Color Code' in attrDict else '',
                                'Size': attrDict['Size'] if 'Size' in attrDict else '',
                                'CostCenter': 'Distrilink',
                                'Quantity': int(line.product_uom_qty) or 0,
                                'EAN': line.product_id.barcode or '',
                                'SKU': line.product_id.default_code or '',
                                'MarketPlace': MarketPlace_code or '',
                                'Customer Email': line.order_id.partner_shipping_id.email or line.order_id.partner_id.email or ' ',
                                'Customer Phone': line.order_id.partner_shipping_id.phone or line.order_id.partner_id.phone or '',
                                'Company': line.order_id.partner_shipping_id.ce_company_name or ''
                            }
                            writer.writerow(values)
                            line.order_id.write(
                                {'is_exported_to_ftp': True, 'state': 'vendor_process', 'vendor_process_date': fields.Datetime.now()})

                csvfile.close()

                ftpConn = conn.connection(conn.ftp_location, conn.ftp_login, conn.password, conn.folder_path)
                ftp = ftpConn['ftp']
                outputDirectory = ftpConn['ftp_folder_path']
                ftp.cwd(outputDirectory)
                with open(file_path, "rb") as f:
                    ftp.storbinary('STOR ' + os.path.basename(csv_file), f)

                os.remove(file_path)
                totalExportedFiles += 1
        cron = self.env.ref('channable_api.ir_cron_export_orders')
        message = ['%s Files are Exported from Odoo to FTP' % (
                        totalExportedFiles)]
        self.env['audit.log'].put_audit_log(cron.name, 'Success', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
