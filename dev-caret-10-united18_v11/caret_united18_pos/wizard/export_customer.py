# -*- coding: utf-8 -*-
import xlwt
from xlsxwriter.workbook import Workbook
import io
from datetime import datetime
import dateutil.parser
import pytz
from pytz import timezone
import base64


from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import tools,models, fields, api, _
from odoo.exceptions import UserError


class PosOrderWizard(models.TransientModel):
    _name = 'customer.export.wizard'
    _description = 'Generate Report'

    start_date = fields.Date(string='Start date')
    end_date = fields.Date(default=fields.Date.today(), string='Last date')

    @api.multi
    def generate_customer_report(self):
        if (not self._context.get('not_date')) and (not self.start_date or not self.end_date):
            raise UserError("Please select start or end date")

        result = []
        # TO DO: check why only read() returning null data
        partners_pos = []
        if self._context.get('not_date'):
            active_ids = self._context.get('active_ids', [])
            partners_pos = self.env['pos.order'].browse(active_ids).mapped('partner_id')
        else:
            partners_pos = self.env['pos.order'].search([
                ('date_order','>=', self.start_date),
                ('date_order','<=', self.end_date)]).mapped('partner_id')
        partners = self.env['res.partner'].search_read(
            [('id','in',partners_pos.ids)],['name','mobile','email'])
        print("partners_pos===================",len(partners_pos))
        filename = 'customer_export_report.xls'
        workbook = xlwt.Workbook()
        style = xlwt.XFStyle()
        style1 = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;') # 36pt
#        ok_style = xlwt.easyxf('pattern: fore_colour light_blue;''font: colour green, bold True;') 
        # Create a font to use with the style
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        font.height = 220
        style.font = font

        font1 = xlwt.Font()
        font1.name = 'Times New Roman'
        font1.bold = True
        font1.height = 260
        style1.font = font1

        # add new colour to palette and set RGB colour value
        xlwt.add_palette_colour("custom_colour", 0x21)
        workbook.set_colour_RGB(0x21, 204, 255, 255)
        
        worksheet = workbook.add_sheet('Sheet 1')
        style2 = xlwt.easyxf('pattern: pattern solid, fore_colour custom_colour')
        font2 = xlwt.Font()
        font2.name = 'Times New Roman'
        font2.bold = True
        font2.height = 220
        style2.font = font2

        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN

        style2.borders = borders

        zero_col = worksheet.col(0)
        zero_col.width = 236 * 25
   
        first_col = worksheet.col(1)
        first_col.width = 236 * 25

        second_col = worksheet.col(2)
        second_col.width = 236 * 25

        worksheet.write(0, 2, tools.ustr('Customer Report'),style1)
        first=worksheet.merge(2,2,1,2)
        worksheet.write(3, 0, tools.ustr('Customer'),style2)
        worksheet.write(3, 1, tools.ustr('Mobile'),style2)
        worksheet.write(3, 2, tools.ustr('Email'),style2)
        row=4
        for partner in partners:
            worksheet.write(row, 0, tools.ustr(partner['name'] or ''))
            worksheet.write(row, 1, tools.ustr(partner['mobile'] or ''))
            worksheet.write(row, 2, tools.ustr(partner['email'] or ''))
            row+=1

        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['customer.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'customer.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return True

class pos_order_excel(models.TransientModel):
    _name= 'customer.excel'
    _description = 'Customer Excel Report'

    excel_file = fields.Binary('Excel Report for Customer')
    file_name = fields.Char('Excel File', size=64)