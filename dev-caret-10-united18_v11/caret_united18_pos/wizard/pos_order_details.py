# -*- coding: utf-8 -*-

from odoo import tools,models, fields, api, _
from odoo.exceptions import UserError
import xlwt
from xlsxwriter.workbook import Workbook
import io
from datetime import datetime
from datetime import date
from datetime import time
import datetime, time
import dateutil.parser
import pytz
from pytz import timezone
from collections import defaultdict
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PosOrderWizard(models.TransientModel):
    _name = 'pos.order.wizard'
    _description = 'Open POS Order Report'

    start_date = fields.Datetime(required=True, string='Start date')
    end_date = fields.Datetime(required=True, default=fields.Datetime.now, string='Last date')
    group_by_customer = fields.Many2one('res.partner', string='Customer', domain="[('customer', '=', True)]")
    sales_person = fields.Many2one('res.users', string='Sales Person')


    @api.onchange('start_date','end_date')
    def date_check(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise UserError(_("Start Date must be less then end date."))

    @api.multi
    def generate_pos_report(self):
        date_end = datetime.datetime.strptime(self.end_date, DEFAULT_SERVER_DATETIME_FORMAT).replace(hour=23,minute=59,second=59)
        print("date_end===========>",date_end)
        result = []
        sales = self.env['pos.order']
        if self.group_by_customer.id and self.sales_person.id == False:
            self.env.cr.execute("""
                SELECT
                    id
                FROM
                    pos_order as pos
                WHERE
                    pos.partner_id = %s
                AND pos.date_order >= %s
                AND pos.date_order <= %s
                AND company_id = %s
                ORDER BY id
        """, (self.group_by_customer.id, self.start_date, date_end, self.env.user.company_id.id))
        elif self.group_by_customer.id and self.sales_person.id:
            self.env.cr.execute("""
                SELECT
                    id
                FROM
                    pos_order as pos
                WHERE
                    pos.partner_id = %s
                AND pos.user_id = %s
                AND pos.date_order >= %s
                AND pos.date_order <= %s
                AND company_id = %s
                ORDER BY id
        """, (self.group_by_customer.id,self.sales_person.id, self.start_date, date_end, self.env.user.company_id.id))
        elif self.sales_person.id and self.group_by_customer.id == False:
            self.env.cr.execute("""
                SELECT
                    id
                FROM
                    pos_order as pos
                WHERE
                    pos.user_id = %s
                AND pos.date_order >= %s
                AND pos.date_order <= %s
                AND company_id = %s
                ORDER BY id
        """, (self.sales_person.id, self.start_date, date_end, self.env.user.company_id.id))
        else:
            self.env.cr.execute("""
                SELECT
                     id
                FROM 
                    pos_order as pos
                WHERE
                    pos.date_order >= %s
                    AND pos.date_order <= %s
                    AND company_id = %s
                ORDER BY id
        """, (self.start_date, date_end, self.env.user.company_id.id))
        sale_id = [res['id'] for res in self.env.cr.dictfetchall()]
        sale_order = sales.sudo().browse(sale_id)
        import base64
        filename = 'POS_export_report.xls'
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
        zero_col.width = 236 * 13
   
        first_col = worksheet.col(1)
        first_col.width = 236 * 30

        second_col = worksheet.col(2)
        second_col.width = 236 * 20

        third_col = worksheet.col(3)
        third_col.width = 236 * 12

        fourth_col = worksheet.col(4)
        fourth_col.width = 236 * 14

        fifth_col = worksheet.col(5)
        fifth_col.width = 236 * 15

        six_col = worksheet.col(6)
        six_col.width = 236 * 15

        worksheet.write(0, 2, tools.ustr('POS Order Report'),style1)
        first=worksheet.merge(2,2,1,2)

        time_zone = self._context.get('tz') or 'Asia/Kolkata'
        fmt = "%Y-%m-%d"


        s_date = pytz.utc.localize(datetime.datetime.strptime(self.start_date,
                                                    DEFAULT_SERVER_DATETIME_FORMAT))
        start_date = s_date.astimezone(timezone(time_zone))
        
        e_date = pytz.utc.localize(datetime.datetime.strptime(str(date_end),
                                                    DEFAULT_SERVER_DATETIME_FORMAT))
        end_date = e_date

        worksheet.write(2, 1, tools.ustr('Start Date : '+start_date.strftime(fmt)),style1)
        worksheet.write(2, 3, tools.ustr('End Date : '+end_date.strftime(fmt)),style1)

        worksheet.write(3, 0, tools.ustr('Order Date'),style2)
        worksheet.write(3, 1, tools.ustr('Order References'),style2)
        worksheet.write(3, 2, tools.ustr('Customer Name'),style2)
        worksheet.write(3, 3, tools.ustr('Payment'),style2)
        worksheet.write(3, 4, tools.ustr('Total Taxes'),style2)
        worksheet.write(3, 5, tools.ustr('Net Amount'),style2)
        worksheet.write(3, 6, tools.ustr('Total Amount'),style2)
        row=4
        tax,total,cash,digital = 0.0,0.0,0.0,0.0
        writeHeader = True
        taxAppend = []
        count = 7
        columIndex = {}
        for sale in sale_order:
            method=''
            for payment in sale.statement_ids:
                if payment.journal_id.name == 'Cash':
                    cash=cash+payment.amount
                if payment.journal_id.name == 'Digital':
                    digital = digital+payment.amount
                if payment.journal_id.name not in method:
                    method=method+payment.journal_id.name+','
            confirm_d = pytz.utc.localize(datetime.datetime.strptime(sale.date_order,
                                                            DEFAULT_SERVER_DATETIME_FORMAT))
            confirm_date = confirm_d.astimezone(timezone(time_zone))
            worksheet.write(row, 0, tools.ustr(confirm_date.date()))
            worksheet.write(row, 1, tools.ustr(sale.name))
            worksheet.write(row, 2, tools.ustr(sale.partner_id.name or ' '))
            worksheet.write(row, 3, tools.ustr(method))
            worksheet.write(row, 4, tools.ustr((round(sale.amount_tax,2))))
            # worksheet.write(row, 5, tools.ustr((round((sale.amount_total-sum(total_tax_list)),2))))
            worksheet.write(row, 6, tools.ustr((round(sale.amount_total,2))))
            currency = sale.pricelist_id.currency_id
            taxList = []
            D = defaultdict(list)
            for line in sale.lines:
                product_taxes = line.product_id.categ_id.tax
                apply_tax_id = False
                if product_taxes:
                    cmp_taxes = self.env['account.tax'].search([('company_id','=',sale.company_id.id)])
                    for t in cmp_taxes:
                        if 'GST Sale' + ' ' + product_taxes + '%' == t.name:
                            apply_tax_id = t

                if sale.fiscal_position_id:
                    taxes = sale.fiscal_position_id.map_tax(apply_tax_id.children_tax_ids, line.product_id, line.order_id.partner_id)
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                if apply_tax_id:
                    taxes = apply_tax_id.children_tax_ids.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)['taxes']
                    taxList += taxes

            for t in taxList:
                D[t['name']].append(t['amount'])
            currency = sale.pricelist_id.currency_id
            for i in sorted(D.keys()):
                if i not in taxAppend:
                    taxAppend.append(i)
                    columIndex[i] = count
                    worksheet.write(3, count, tools.ustr(i),style2)
                    count += 1
            total_tax_list = []
            for k, v in D.items():
                if columIndex.get(k):
                    worksheet.write(row, columIndex[k], currency.round(sum(v)))
                    total_tax_list.append(sum(v))
            worksheet.write(row, 5, tools.ustr((round((sale.amount_total-sum(total_tax_list)),2))))
            row+=1
            tax = tax + sale.amount_tax
            tax_list = total_tax_list
            total = total + sale.amount_total

        worksheet.write(row+2, 1, tools.ustr('Cash Total'),style1)
        worksheet.write(row+3, 1, tools.ustr('Digital Total'),style1)
        worksheet.write(row+4, 1, tools.ustr('Total'),style1)
        worksheet.write(row+2, 5, tools.ustr('+'+str(cash)),style1)
        worksheet.write(row+3, 5, tools.ustr('+'+str(digital)),style1)
        worksheet.write(row+4, 4, tools.ustr((round(tax,2))),style1)
        worksheet.write(row+4, 5, tools.ustr((round(total,2))),style1)

        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['pos.order.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'pos.order.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return True

class pos_order_excel(models.TransientModel):
    _name= "pos.order.excel"
    _description = "Pos Order Excel Report"

    excel_file = fields.Binary('Excel Report for POS Order')
    file_name = fields.Char('Excel File', size=64)

class ProductCategoryTax(models.Model):
    _inherit = 'product.category'

    tax = fields.Selection([
        ('5', '5%'),
        ('10', '10%'),
        ('15', '15%'),
        ('18', '18%'),
        ('20', '20%')
    ], string='Tax')