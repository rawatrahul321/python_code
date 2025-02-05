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
    _name = 'ftp.connection'
    _description = 'FTP Connection'

    name = fields.Char('Name of Location')
    location_type = fields.Selection([
        ('order_export', 'Order Export'),
        ('stock_import', 'Stock Import'),
        ('shipping_import', 'Shipping Import')
    ])
    ftp_location = fields.Char('FTP Location')
    folder_path = fields.Char('Folder Path')
    ftp_login = fields.Char('FTP Accounts')
    password = fields.Char('Password')
    delimiter = fields.Char('Delimiter', size=1)

    _sql_constraints = [('location_type_unique', 'unique(location_type)', 
                     'This location type is already created, please create another one.')]

    def connection(self, ftp_location, ftp_login, password, folder_path):
        try:
            ftp = AuthorizeFTP(ftp_location, ftp_login, password, folder_path)
            return ftp.ftpConnection()
        except Exception as e:
            raise UserError(_("Make Sure FTP Configuration Details are Valid."))

    @api.multi
    def test_ftp_connection(self):
        for server in self:
            try:
                ftpConn = server.connection(server.ftp_location, server.ftp_login, server.password, server.folder_path)
            except:
                raise UserError(_('Make Sure FTP Login Details and FTP Location are Valid.'))

            ftp = ftpConn['ftp']
            folderName = ftpConn['ftp_folder_path']

            try:
                ftp.cwd(folderName)
            except:
                raise UserError(_('Please Confirm Your Folder Path is Valid.'))

            raise UserError(_('Connection Test Succeeded! Everything seems properly set up!'))

    def getBarcode(self, url):
        """We assume that biggest continuious digits are barcode from url."""
        allDigitGroup = re.findall(r'[0-9]+', url)
        return sorted(allDigitGroup, key=lambda x: len(x), reverse=True)[0] if allDigitGroup else None

    def fbm_process_flow(self):
        """process order flow with FBA/FBB flag and update stock warehouse based on that"""
        orders = self.env['sale.order'].search([('state', '=', 'channable_order')])
        export_products = []
        fbm_orders = 0
        invMessage = ''
        for order in orders:
            for line in order.order_line:
                if (line.product_id.is_fba and
                    (line.order_id.channable_channel_id and 'Amazon' in line.order_id.channable_channel_id.name)):
                    wh_location = self.env['stock.location'].search([('name', '=', 'WH')])
                    stock_quant = self.env['stock.quant'].search([
                        ('product_id', '=', line.product_id.id),
                        ('location_id.usage', '=', 'internal'),
                        ('location_id.location_id', '!=', wh_location.id)
                    ], limit=1)
                    warehouse = False
                    if stock_quant:
                        warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', stock_quant.location_id.id)])
                    if warehouse:
                        order.warehouse_id = warehouse.id
                    else:
                        order.warehouse_id = self.env.ref('channable_api.amazon_eu_warehouse').id
                    order.is_fbm_order = True
                elif (line.product_id.is_fbb and
                    (line.order_id.channable_channel_id and 'Bol' in line.order_id.channable_channel_id.name)):
                    order.warehouse_id = self.env.ref('channable_api.bol_warehouse').id
                    order.is_fbm_order = True
                else:
                    export_products.append(line.product_id.id)
            if order.is_fbm_order:
                fbm_orders += 1
                order.action_confirm()
                for picking in order.picking_ids:
                    try:
                        res = picking.button_validate()
                    except Exception as e:
                        if picking.state != 'done':
                            order.write({'delivery_validate_error': e})
                invoice_id = order.action_invoice_create()
                invoice = self.env['account.invoice'].browse(invoice_id)
                invoice.action_invoice_open()
                invoice.sale_order_id = order.id
                invoice.send_invoice_mail()
                journal = self.env['account.journal'].search([('is_pay_channable_invoice', '=', True)], limit=1)
                if journal:
                    if invoice.state == 'open':
                        invoice.moveInvoiceToPaid(invoice, journal)
                else:
                    invMessage = 'Invoice is not go to Paid state because journal are not Configured'
        self.exportOrders(export_products)
        cron = self.env.ref('channable_api.ir_cron_export_orders')
        message = ['%s Orders are FBM Orders' % (fbm_orders)]
        if invMessage:
            message.append(invMessage)
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)


    def exportOrders(self, product_ids):
        header = ['Odoo Order ID', 'Market Place Order Id', 'Customer Name', 'Street', 'Street 2', 'House Number',
            'House Number EXT', 'Address Supplement', 'City', 'Zip Code', 'Country Code', 'Order Date', 'Product Name',
            'Item Code', 'Color Code', 'Size', 'CostCenter', 'Quantity', 'EAN', 'SKU', 'MarketPlace', 'Customer Email', 'Customer Phone']

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
                                'Customer Phone': line.order_id.partner_shipping_id.phone or line.order_id.partner_id.phone or ''
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

    def createTempCSV(self, file, ftp):
        fileName = file.split('/')[1]
        file_fd, file_path = tempfile.mkstemp(prefix=fileName)

        with open(file_path, 'w+b') as writeFile:
            res = ftp.retrbinary("RETR " + file, writeFile.write)
        writeFile.close()

        return file_path

    def importStock(self):
        conn = self.search([('location_type', '=', 'stock_import')])
        ftpConn = conn.connection(conn.ftp_location, conn.ftp_login, conn.password, conn.folder_path)
        ftp = ftpConn['ftp']
        inputDirectory = ftpConn['ftp_folder_path']

        files = ftp.nlst(inputDirectory)
        ## for move stock file to archive folder
        filepathSource = []
        archiveDir = ''
        proceedFileCount = 0
        allFilesStock = {}
        for file in files:
            allData = []
            def getStockData(data):
                allData.append(data)

            if 'stock.csv' in file:
                ftp.retrbinary("RETR " + file, getStockData, blocksize=1000)
                ## for move stock file to archive folder
                filepathSource.append(file)
                proceedFileCount += 1
            if 'archive' in file:
                archiveDir = file

            stockList = [i for i in allData]
            res = b"".join(stockList)
            # stockData = res.decode("utf-8").split('\r\n')
            stockData = re.split('\r\n|\n|', res.decode("utf-8"))
            for stock in stockData:
                value = [x.strip() for x in stock.split(conn.delimiter or ';')]
                if len(value) > 1:
                    barcode = value[0]
                    try:
                        value[1] = max(int(float(value[1])), 0)
                    except:
                        value[1] = 0
                    stockQty = value[1]
                    allFilesStock[barcode] = stockQty

        missingBarcodes = []
        for barcode, stockQty in allFilesStock.items():
            product = self.env['product.product'].search([('barcode', '=', barcode)])
            if product:
                changeQty = self.env['stock.change.product.qty'].create({
                    'product_id': product.id,
                    'new_quantity': stockQty,
                })
                changeQty.change_product_qty()
                product.write({'qty_available': stockQty})
            else:
                missingBarcodes.append(barcode)
        if 'EAN' in missingBarcodes:
            missingBarcodes.remove('EAN')

        ## this is for move stock file to archive folder
        self.moveFilesToArchvie(filepathSource, archiveDir, ftp)
        cron = self.env.ref('channable_api.ir_cron_import_stock')
        message = ['%s %s Stock Files are Imported from FTP to Odoo.' % (
                        proceedFileCount, filepathSource)]
        if missingBarcodes:
            message.append(' %s Barcodes are available in FTP Stock files but Missing in Odoo' % list(set(missingBarcodes)))
        self.env['audit.log'].put_audit_log(cron.name, 'Success', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
        ftp.close()

    def moveFilesToArchvie(self, sourcePath, destinationPath, ftp):
        for sourceFile in sourcePath:
            file_name = (sourceFile.split('/')[1]).split('.')
            if len(file_name) > 1:
                proceedFile = file_name[0] + '_processed.' + file_name[1]
            else:
                proceedFile = file_name[0] + '_processed'
            destinationFile = destinationPath + '/' + proceedFile
            ftp.rename(sourceFile, destinationFile)

    def importShippingFiles(self):
        shippingFileObj = self.env['ftp.shipping.file']
        conn = self.search([('location_type', '=', 'shipping_import')])
        ftpConn = conn.connection(conn.ftp_location, conn.ftp_login, conn.password, conn.folder_path)
        ftp = ftpConn['ftp']
        inputDirectory = ftpConn['ftp_folder_path']
        cron = self.env.ref('channable_api.ir_cron_import_shipping_files')
        try:
            files = ftp.nlst(inputDirectory)
            ## for move stock file to archive folder
            filepathSource = []
            shippingarchiveDir = ''
            proceedFileCount = 0
            for file in files:
                fileName = file.split('/')[1]
                if not fileName.startswith('archive'):
                    file_path = conn.createTempCSV(file, ftp)

                    result_file = open(file_path, 'rb').read()
                    md5 = hashlib.md5(base64.encodestring(result_file)).hexdigest()
                    shippingFile = shippingFileObj.search([('name', '=', fileName), ('file_md5', '=', md5)])
                    if not shippingFile:
                        shippingFileObj.create({
                            'name': fileName,
                            'import_date': datetime.datetime.now(),
                            'shipping_file': base64.encodestring(result_file),
                            'status': 'progress',
                            'file_md5': md5
                        })
                        proceedFileCount += 1
                    filepathSource.append(file)
                    os.remove(file_path)

                ## for move stock file to archive folder
                if 'archive' in file:
                    shippingarchiveDir = file

            ##this is for move stock file to archive folder
            self.moveFilesToArchvie(filepathSource, shippingarchiveDir, ftp)
            message = ['%s Shipping Files are Created in Odoo from FTP' % (
                                proceedFileCount)]
            self.env['audit.log'].put_audit_log(cron.name, 'Success', '', message[0])
            self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
        except:
            self.env['audit.log'].put_audit_log(cron.name, 'Failed', '', 'Please Confirm Your Folder Path is Valid.')
            raise UserError(_('Please Confirm Your Folder Path is Valid.'))

    def importShippingInfo(self):
        shippingFiles = self.env['ftp.shipping.file'].search([('status', '=', 'progress')])
        conn = self.search([('location_type', '=', 'shipping_import')])
        cron = self.env.ref('channable_api.ir_cron_import_shipping')
        OrderCount = 0
        validateDelivery = 0
        notValidateDelivery = 0
        skipOrderCount = []
        invMessage = ''
        for file in shippingFiles:
            if file.shipping_file and conn:
                inputx = io.BytesIO()
                inputx.write(base64.decodebytes(file.shipping_file))
                inputx.seek(0)
                shippingData = inputx.getvalue().decode('ISO-8859-1').split('\n')
                for shipping in shippingData:
                    shippingInfo = shipping.split(conn.delimiter or '|')
                    if len(shippingInfo) > 1:
                        channableChannel = self.env['channable.order.channel'].search([
                            ('channel_id', '=', shippingInfo[0])])
                        if channableChannel:
                            orders = self.env['sale.order'].search([
                                ('channable_channel_id', '=', channableChannel.id), ('state', '=', 'vendor_process')])
                            for order in orders:
                                skipOrder = False
                                for line in order.order_line:
                                    if line.product_id.channable_vendor_ids and not line.product_id.channable_vendor_ids.name.courier_name:
                                        skipOrder = order.name
                                        skipOrderCount.append(order.name)
                                        self.env['audit.log'].put_audit_log(cron.name, 'Failed', '',
                                            'Please Set Courier Name on Vendor for Product (%s)' % line.product_id.name)
                                        logger.warning(_("Please Set Courier Name on Vendor for Product (%s)" % line.product_id.name))

                                if not skipOrder == order.name:
                                    vendor_ids = [line.product_id.channable_vendor_ids.name.id for line in order.order_line
                                                    if line.product_id.channable_vendor_ids]
                                    transporterList = []
                                    if all(elem == vendor_ids[0] for elem in vendor_ids):
                                        for line in order.order_line:
                                            if line.product_id.channable_vendor_ids:
                                                transporterList.append(line.product_id.channable_vendor_ids.name.courier_name)
                                    else:
                                        self.env['audit.log'].put_audit_log(
                                            cron.name, 'Failed', '', 'Products are in sale order lines from different vendors')
                                        logger.warning(_("Products are in sale order lines from different vendors"))

                                    transporter = list(set(transporterList))

                                    barcode = conn.getBarcode(shippingInfo[1])
                                    tracking_url = shippingInfo[1]

                                    if tracking_url and barcode and transporter:
                                        order.action_confirm()
                                        OrderCount += 1
                                        for picking in order.picking_ids:
                                            picking.write({
                                                'tracking_url': tracking_url,
                                                'tracking_code': barcode,
                                                'transporter': transporter[0] or '',
                                                'is_delivery_not_validated': True
                                            })
                                            try:
                                                res = picking.button_validate()
                                                if res == 1:
                                                    picking.write({'is_delivery_not_validated': False})
                                                    validateDelivery += 1
                                            except Exception as e:
                                                if picking.state != 'done':
                                                    order.write({'delivery_validate_error': e})
                                                    notValidateDelivery += 1
                                                    self.env['audit.log'].put_audit_log(
                                                        cron.name, 'Failed', '', str(e))
                                                    logger.exception(str(e))
                                        invoice_id = order.action_invoice_create()
                                        invoice = self.env['account.invoice'].browse(invoice_id)
                                        invoice.action_invoice_open()
                                        invoice.sale_order_id = order.id
                                        invoice.send_invoice_mail()
                                        journal = self.env['account.journal'].search([('is_pay_channable_invoice', '=', True)], limit=1)
                                        if journal:
                                            if invoice.state == 'open':
                                                invoice.moveInvoiceToPaid(invoice, journal)
                                        else:
                                            invMessage = 'Invoice is not go to Paid state because journal are not Configured'
                                            self.env['audit.log'].put_audit_log(cron.name, 'Failed', '', invMessage)
                                    else:
                                        self.env['audit.log'].put_audit_log(
                                            cron.name, 'Failed', '', 'Please Fill Proper Tracking Details')
                                        order.write({'delivery_validate_error': 'Please Fill Proper Tracking Details'})

            file.write({'status': 'proceed'})
        message = ['%s Orders are Confirmed and %s Delivery are Validated %s are Remain for Manual Process. ' % (
            OrderCount, validateDelivery, notValidateDelivery)]
        if skipOrderCount:
            message.append('%s Orders are not Confirmed because transporter Name is not set on Vendor.' % skipOrderCount)
        self.env['audit.log'].put_audit_log(cron.name, 'Success', '', message[0])
        if invMessage:
            message.append(invMessage)
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def shipping_update_to_channable(self):
        validatedPickings = 0
        pickings = self.env['stock.picking'].search([
            ('state', 'not in', ['done', 'cancel']), ('is_delivery_not_validated', '=', True)
        ])
        for picking in pickings:
            try:
                res = picking.button_validate()
                if res == 1:
                    picking.write({'is_delivery_not_validated': False})
                    validatedPickings += 1
            except Exception as e:
                if picking.state != 'done':
                    picking.sale_id.write({'delivery_validate_error': e})
                    logger.exception(str(e))
        cron = self.env.ref('channable_api.ir_cron_channable_shipping_update')
        message = ['%s Delivery are Validated. ' %(validatedPickings)]
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
