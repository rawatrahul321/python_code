# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import tempfile
import werkzeug
import csv
import base64

from odoo import http
from odoo.http import request

class StockUrlController(http.Controller):
    @http.route('/distrilink_csv_stock', type='http', auth='public')
    def download_stock_csv(self, **kw):
        """ Returns CSV File of csv stock export (EAN(Barcode),
        SKU(internal Reference), Stock(on Hand)"""

        filename = 'stock_export.csv'
        file_fd, file_path = tempfile.mkstemp(suffix='.csv', prefix='stock_export')
        csv_data = []
        # locations = request.env['stock.location'].sudo().search([('name', 'in', ['WH', 'AAVWH'])])
        # stock_quants = request.env['stock.quant'].sudo().search([('location_id.location_id', 'in', locations.ids)])
        query = """
            SELECT p.barcode, p.default_code, sum(sq.quantity)
            FROM stock_quant sq
            INNER JOIN product_product p
            ON sq.product_id = p.id
            INNER JOIN stock_location sl
            ON sq.location_id = sl.id
            WHERE sl.location_id IN (SELECT id FROM stock_location
                WHERE name IN ('WH', 'AAVWH'))
            GROUP BY p.barcode, p.default_code;
        """
        request.env.cr.execute(query, kw)
        list_data = request.env.cr.fetchall()
        product_ids = request.env['product.product'].sudo().search([
            ('type', '=', 'product'), ('barcode', '!=', False)])
        barcode_list = []
        for product in product_ids:
            for data in list_data:
                if  product.barcode == data[0]:
                    csv_data.append(data)
                    barcode_list.append(data[0])
            if product.barcode not in barcode_list:
                result = (
                    product.barcode or '',
                    product.default_code or '',
                    0
                )
                csv_data.append(result)

        # for stock in stock_quants:
        #     result = [
        #         stock.product_id.barcode or '',
        #         stock.product_id.default_code or '',
        #         int(stock.quantity) or 0
        #     ]
        #     csv_data.append(result)
        # product_ids = request.env['product.product'].sudo().search([
        #     ('type', '=', 'product'), ('location_id', 'in', locations.ids)])
        # for product in product_ids:
        #     # print ('product location...............', product.location_id)
        #     result = [
        #         product.barcode or '',
        #         product.default_code or '',
        #         int(product.qty_available) or 0
        #     ]
        #     csv_data.append(result)

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
        csv_rec = request.env['csv.stock'].sudo().create(
			{'csv_file': base64.encodestring(result_file), 'file_name': filename})

        if csv_rec.id:
            url = 'web/content/?model=csv.stock&download=true&field=csv_file&id=%s&filename=%s' % (
                    csv_rec.id, filename)
            return werkzeug.utils.redirect(url)
