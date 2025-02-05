# -*- coding: utf-8 -*-
import xlwt
from xlsxwriter.workbook import Workbook
import io
from datetime import datetime
import dateutil.parser
import pytz
from pytz import timezone
import base64
from collections import defaultdict
from operator import itemgetter
import itertools


from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import tools,models, fields, api, _
from odoo.exceptions import UserError

class PosDiscountWizard(models.TransientModel):
    _name = 'pos.discount.wizard'
    _description = 'Generate Report'

    start_date = fields.Date(string='Start date')
    end_date = fields.Date(default=fields.Date.today(), string='Last date')

    @api.multi
    def generate_pos_discount_report(self):
        if (not self._context.get('not_date')) and (not self.start_date or not self.end_date):
                raise UserError("Please select start or end date")

        posPromotionProduct = self.env['pos.promotion'].sudo().search([]).mapped('discount_product').ids
        fields = ['product_id', 'price_subtotal_incl','order_id','company_id']
        pos_order_lines = self.env['pos.order.line'].sudo().search_read(
            [('order_id.state','not in',['draft','cancel']),
            ('order_id.date_order','>=',self.start_date),
            ('order_id.date_order','<=',self.end_date)],fields)
        # print("pos_order_lines===============",len(pos_order_lines))
        D = defaultdict(list)
        orderObj = self.env['pos.order']
        partnerObj = self.env['res.partner']
        order_fields = ['partner_id','date_order']
        partner_fields = ['mobile']
        count = 1
        for line in pos_order_lines:
            order_read = orderObj.sudo().browse(line['order_id'][0]).read(order_fields)
            partner_mobile = partnerObj.sudo().browse(order_read[0]['partner_id'] and order_read[0]['partner_id'][0]).read(['mobile']) or ''
            count += 1
            # print("count====================",count)
            D[line['company_id']].append([
                line['order_id'], 
                order_read[0]['partner_id'] and order_read[0]['partner_id'][1],
                line['price_subtotal_incl'],
                partner_mobile and partner_mobile[0]['mobile'] or '',
                order_read[0]['date_order'],
                line['product_id'][0]])

        for k, v in dict(D).items():
            l = []
            keyfunc = lambda t: (t[0],t[1])
            v.sort(key=keyfunc)
            for key, rows in itertools.groupby(v, keyfunc):
                Total = 0.0
                discount = 0.0
                woDisTotal = 0.0
                for r in rows:
                    if r[5] in posPromotionProduct:
                        discount += r[2]
                    else:
                        woDisTotal += r[2]
                Total += (woDisTotal-abs(discount))
                l.append((key[0],key[1], r[3], r[4], woDisTotal, discount, Total))
            D[k] = l

        filename = 'pos_discount_report.xls'
        workbook = xlwt.Workbook()
        style = xlwt.XFStyle()
        style1 = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;')

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
        style2 = xlwt.easyxf('pattern: pattern solid,fore_colour custom_colour')
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
        zero_col.width = 236 * 50
   
        first_col = worksheet.col(1)
        first_col.width = 236 * 25

        second_col = worksheet.col(2)
        second_col.width = 236 * 25

        third_col = worksheet.col(3)
        third_col.width = 236 * 25

        fourth_col = worksheet.col(4)
        fourth_col.width = 236 * 25

        fifth_col = worksheet.col(5)
        fifth_col.width = 236 * 25

        sixth_col = worksheet.col(6)
        sixth_col.width = 236 * 25

        worksheet.write(0, 2, tools.ustr('POS Discount Report'),style1)
        first=worksheet.merge(2,2,1,2)
        worksheet.write(3, 0, 'Total Company',style2)
        worksheet.write(3, 1, len(D),style2)
        worksheet.write(5, 0, tools.ustr('Company'),style2)
        worksheet.write(5, 1, tools.ustr('Customer'),style2)
        worksheet.write(5, 2, tools.ustr('Mobile'),style2)
        worksheet.write(5, 3, tools.ustr('Order Date'),style2)
        worksheet.write(5, 4, tools.ustr('Total Without Discount'),style2)
        worksheet.write(5, 5, tools.ustr('Discount'),style2)
        worksheet.write(5, 6, tools.ustr('Total With Discount'),style2)
        
        
        row=6
        gTotalWoDis = 0.0
        gtotal = 0.0
        gTotalDis = 0
        for key, values in D.items():
            cTotalWoDis = 0.0
            ctotal = 0.0
            cTotalDis = 0.0
            row += 1
            worksheet.write(row, 0, tools.ustr(key[1]),style)
            for vdata in values:
                # print("vdata======================",vdata)
                row += 1
                worksheet.write(row, 1, vdata[1] and tools.ustr(vdata[1]) or '')
                worksheet.write(row, 2, vdata[2])
                worksheet.write(row, 3, vdata[3])
                worksheet.write(row, 4, vdata[4])
                worksheet.write(row, 5, vdata[5])
                worksheet.write(row, 6, vdata[6])
                cTotalWoDis += vdata[4]
                cTotalDis += vdata[5]
                ctotal += vdata[6]
            row += 1
            worksheet.write(row, 3, 'Total', style)
            worksheet.write(row, 4, cTotalWoDis, style)
            worksheet.write(row, 5, cTotalDis, style)
            worksheet.write(row, 6, ctotal, style)
            row+=1
            gTotalWoDis += cTotalWoDis
            gTotalDis += cTotalDis
            gtotal += ctotal
        row+=1
        worksheet.write(row, 3, 'Grand Total', style)
        worksheet.write(row, 4, gTotalWoDis, style)
        worksheet.write(row, 5, gTotalDis, style)
        worksheet.write(row, 6, gtotal, style)
        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['aspl.pos.discount'].create({
            'excel_file': base64.encodestring(fp.getvalue()),
            'file_name': filename})
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'aspl.pos.discount',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return True


class PosDiscountExcel(models.TransientModel):
    _name= 'aspl.pos.discount'
    _description = 'Pos Discount Excel Report'

    excel_file = fields.Binary('Excel Report for POS Discount')
    file_name = fields.Char('Excel File', size=64)
