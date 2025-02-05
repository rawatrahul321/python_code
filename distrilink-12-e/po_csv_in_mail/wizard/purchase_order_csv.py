# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import csv
import os
import tempfile
import base64

from odoo import api, fields, models, _

class PurchaseOrderCsv(models.TransientModel):
    _name = 'purchase.order.csv'
    _description = 'Purchase Order CSV'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')

    def attach_purchase_order_line_csv(self):
        if self.purchase_order_id:
            csv_data = []
            header = ['Product Name', 'SKU', 'EAN', 'Ordered Qty']
            file_fd, file_path = tempfile.mkstemp(suffix='.csv', prefix='purchase_order')
            for line in self.purchase_order_id.order_line:
                data = [line.product_id.name if line.product_id and line.product_id.name else '',
                    str(line.product_id.default_code) if line.product_id and line.product_id.default_code else '',
                    str(line.product_id.barcode) if line.product_id and line.product_id.barcode else '',
                    int(line.product_qty) if line.product_qty else 0
                ]
                csv_data.append(data)

            with open(file_path, "w") as writeFile:
                writer = csv.writer(writeFile)
                # write the header
                writer.writerow(header)
                # write multiple rows
                writer.writerows(csv_data)
            writeFile.close()

            result_file = open(file_path, 'rb').read()
            attachment_id = self.env['ir.attachment'].create({
                'name': 'Purchase Order - %s.csv'%(self.purchase_order_id.name),
                'datas': base64.encodestring(result_file),
                'type': 'binary',
                'datas_fname': 'Purchase Order - %s.csv'%(self.purchase_order_id.name),
                'res_model': 'mail.compose.message',
            })
            try:
                os.unlink(file_path)
            except (OSError, IOError):
                _logger.error('Error when trying to remove file %s' % file_path)
            return attachment_id
