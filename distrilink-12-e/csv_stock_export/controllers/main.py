# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import http
from odoo.http import request
import tempfile

import werkzeug

import csv
import base64


class CsvStockReport(http.Controller):

    @http.route('/csv_stock_report', type='http', auth='none')
    def csv_stock_report(self, **kw):
        """ Returns CSV File of csv stock export (EAN(Barcode), 
        SKU(internal Reference), Stock(on Hand)"""

        filename = 'stock_export.csv'
        file_fd, file_path = tempfile.mkstemp(suffix='.csv', prefix='stock_export')
        csv_data = []
        product_ids = request.env['product.product'].sudo().search([('type', '=', 'product')])
        for product in product_ids:
            result = [
                product.barcode or '',
                product.default_code or '',
                product.qty_available or 0
            ]
            csv_data.append(result)

        with open(file_path, "w") as writeFile:
            writer = csv.writer(writeFile, delimiter=';')
            writer.writerows([[
                'EAN',
                'SKU',
                'Stock'
            ]])
            writer.writerows(csv_data)
        writeFile.close()

        result_file = open(file_path, 'rb').read()
        csv_rec = request.env['csv.stock'].sudo().create({'csv_file': base64.encodestring(result_file), 'file_name': filename})

        if csv_rec.id:
            url =  'web/content/?model=csv.stock&download=true&field=csv_file&id=%s&filename=%s' % (
                    csv_rec.id, filename),
            return werkzeug.utils.redirect(url[0])

