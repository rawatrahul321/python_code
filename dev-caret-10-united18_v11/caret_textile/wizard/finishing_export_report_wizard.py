# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of HiTechnologia (Website: www.hitechnologia.com)                     #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################
from datetime import datetime
from odoo import models, fields, api
import csv
import xlwt
from io import BytesIO
from io import StringIO

class FinishingExportWizard(models.TransientModel):
    _name = 'finishing.export.wizard'
    _description = 'Finishing Export Wizard'

    @api.multi
    def export_finishing_excel(self):
        ProductionObj = self.env['production.process']
        FinishingOrderLineObj = self.env['finishing.order.line']
        result = []
        ActiveIds = self._context.get('active_ids')
        if len(ActiveIds) > 0:
            for finish in ProductionObj.browse(ActiveIds):
                if finish.fabric_color_type == 'color' or (finish.fabric_color_type == 'noncolor' and not finish.finishing_colour_ids):
                    for line in finish.finishing_ids:
                        result.append({
                            'Name': line.product_id and line.product_id.name or '',
                            'Article': line.lot_id and line.lot_id.name or '',
                            'MRP': float(format(line.mrp, '.2f')),
                            'Color': line.color_id and line.color_id.name or '',
                            'Size': line.size_id and line.size_id.name or '',
                                })
                elif finish.fabric_color_type == 'noncolor' and finish.finishing_colour_ids:
                    for line in finish.finishing_colour_ids:
                        result.append({
                            'Name': line.product_id and line.product_id.name or '',
                            'Article': line.lot_id and line.lot_id.name or '',
                            'MRP': float(format(line.mrp, '.2f')),
                            'Color': line.colour_id and line.colour_id.name or '',
                            'Size': line.size_id and line.size_id.name or '',
                                })

        import base64
        filename = 'Finishing.xls'
        workbook = xlwt.Workbook()
        style = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;') # 36pt
        ok_style = xlwt.easyxf('font: colour black, bold True;') 
        # Create a font to use with the style
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        font.height = 250
        style.font = font
        worksheet = workbook.add_sheet('Sheet 1')
        #worksheet.write(0,2, 'Export Invoice', style)

        second_col = worksheet.col(1)
        second_col.width = 236 * 40

        worksheet.write(0, 0, 'Name',ok_style)
        worksheet.write(0, 1, 'Article',ok_style)
        worksheet.write(0, 2, 'MRP',ok_style)
        worksheet.write(0, 3, 'Color',ok_style)
        worksheet.write(0, 4, 'Size',ok_style)
        row = 1
        for val in result:
            worksheet.write(row, 0, val['Name'])
            worksheet.write(row, 1, val['Article'])
            worksheet.write(row, 2, val['MRP'])
            worksheet.write(row, 3, val['Color'])
            worksheet.write(row, 4, val['Size'])
            row+=1

        buffer = BytesIO()
        workbook.save(buffer)
        export_id = self.env['finish.export.excel'].create({'excel_file': base64.encodestring(buffer.getvalue()), 'file_name': filename})
        buffer.close()
        
        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'finish.export.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }



class finish_export_excel(models.TransientModel):
    _name= "finish.export.excel"
    _description = "Finishing Excel Report"

    excel_file = fields.Binary('Report for Finishing')
    file_name = fields.Char('File', size=64)