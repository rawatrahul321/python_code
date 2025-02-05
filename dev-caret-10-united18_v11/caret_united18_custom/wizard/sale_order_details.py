# -*- coding: utf-8 -*-

from odoo import tools,models, fields, api, _
from odoo.exceptions import UserError
import xlwt
from xlsxwriter.workbook import Workbook
import io
from datetime import datetime
import dateutil.parser

class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'
    _description = 'Open Sale Order Report'

    start_date = fields.Datetime(required=True, string='Start date')
    end_date = fields.Datetime(required=True, default=fields.Datetime.now, string='Last date')
    group_by_customer = fields.Many2one('res.partner', string='Customer', domain="[('customer', '=', True)]")
    state = fields.Selection([
            ('sale', 'Sales Order'),
            ('done', 'Locked'),
            ],required=True, string='Status', default='sale')
    sales_person = fields.Many2one('res.users', string='Sales Person')
    show_payment_details = fields.Boolean('Payment Details')

    @api.onchange('start_date','end_date')
    def date_check(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise UserError(_("Start Date must be less then end date."))

    @api.multi
    def generate_sale_report(self):
        result = []
        payment_obj = self.env['account.payment']

        if self.group_by_customer.id and self.sales_person.id == False:
            self.env.cr.execute("""
                SELECT
                    confirmation_date,
                    name,
                    amount_tax,
                    amount_untaxed,
                    amount_total
                FROM
                    sale_order as sale
                WHERE
                    sale.partner_id = %s
                AND sale.state = %s
                AND sale.confirmation_date >= %s
                AND sale.confirmation_date <= %s
                ORDER BY confirmation_date
        """, (self.group_by_customer.id, self.state, self.start_date, self.end_date))
        elif self.group_by_customer.id and self.sales_person.id:
            self.env.cr.execute("""
                SELECT
                    confirmation_date,
                    name,
                    amount_tax,
                    amount_untaxed,
                    amount_total
                FROM
                    sale_order as sale
                WHERE
                    sale.partner_id = %s
                AND sale.user_id = %s
                AND sale.state = %s
                AND sale.confirmation_date >= %s
                AND sale.confirmation_date <= %s
                ORDER BY confirmation_date
        """, (self.group_by_customer.id,self.sales_person.id, self.state, self.start_date, self.end_date))
        elif self.sales_person.id and self.group_by_customer.id == False:
            self.env.cr.execute("""
                SELECT
                    confirmation_date,
                    name,
                    amount_tax,
                    amount_untaxed,
                    amount_total
                FROM
                    sale_order as sale
                WHERE
                    sale.user_id = %s
                AND sale.state = %s
                AND sale.confirmation_date >= %s
                AND sale.confirmation_date <= %s
                ORDER BY confirmation_date
        """, (self.sales_person.id, self.state, self.start_date, self.end_date))
        else:
            self.env.cr.execute("""
                SELECT
                    confirmation_date,
                    name,
                    amount_tax,
                    amount_untaxed,
                    amount_total
                FROM 
                    sale_order as sale
                WHERE
                    sale.confirmation_date >= %s
                    AND sale.confirmation_date <= %s
                    AND sale.state = %s
                    AND sale.company_id = %s
                ORDER BY confirmation_date
        """, (self.start_date, self.end_date, self.state,self.env.user.company_id.id))
        sale_data = [res for res in self.env.cr.dictfetchall()]
        if self.show_payment_details == True and self.group_by_customer.id:
            self.env.cr.execute("""
                SELECT
                     payment_date as confirmation_date,
                     name,
                     amount
                FROM
                    account_payment as payment
                WHERE
                    payment.payment_date >= %s
                    AND payment.payment_date <= %s
                    AND payment.state = %s
                    AND payment.partner_id = %s
                    AND payment.company_id = %s
                ORDER BY payment_date
        """, (self.start_date,self.end_date,'posted', self.group_by_customer.id,self.env.user.company_id.id))
        if self.show_payment_details == True and self.group_by_customer.id == False:
            self.env.cr.execute("""
                SELECT
                     payment_date as confirmation_date,
                     name,
                     amount
                FROM
                    account_payment as payment
                WHERE
                    payment.payment_date >= %s
                    AND payment.payment_date <= %s
                    AND payment.state = %s
                    AND company_id = %s
                ORDER BY payment_date
        """, (self.start_date,self.end_date,'posted',self.env.user.company_id.id))
        if self.show_payment_details == True:
            payment_details = [res for res in self.env.cr.dictfetchall()]
            for number in range(len(payment_details)):
                sale_data.append(payment_details[number])
        sales = sorted(sale_data, key=lambda item: item['confirmation_date'])
        import base64
        filename = 'sales_export_report.xls'
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
        zero_col.width = 236 * 12
   
        first_col = worksheet.col(1)
        first_col.width = 236 * 35

        second_col = worksheet.col(2)
        second_col.width = 236 * 15

        third_col = worksheet.col(3)
        third_col.width = 236 * 15

        fourth_col = worksheet.col(4)
        fourth_col.width = 236 * 15

        fifth_col = worksheet.col(5)
        fifth_col.width = 236 * 15

        six_col = worksheet.col(6)
        six_col.width = 236 * 15

        if self.show_payment_details == False:
            worksheet.write(0, 2, tools.ustr('Sales Order Report'),style1)
        else:
            worksheet.write(0, 2, tools.ustr('Customer Statement'),style1)
        if self.group_by_customer:
            worksheet.write(3, 2, tools.ustr('Customers : '+self.group_by_customer.name),style1)
        else:
            worksheet.write(3, 2, tools.ustr('Customers :'),style1)
        worksheet.write(2, 1, tools.ustr('Start Date : '+self.start_date),style1)
        worksheet.write(2, 3, tools.ustr('End Date : '+self.end_date),style1)

        worksheet.write(4, 0, tools.ustr('Order Date'),style2)
        worksheet.write(4, 1, tools.ustr('Order References'),style2)
        worksheet.write(4, 2, tools.ustr('Total Taxes'),style2)
        worksheet.write(4, 3, tools.ustr('Sub Total'),style2)
        worksheet.write(4, 4, tools.ustr('Total Amount'),style2)
        worksheet.write(4, 5, tools.ustr('Credit Amount'),style2)
        row=5
        tax,due,total,credit = 0.0,0.0,0.0,0.0
        for number in range(len(sales)):
            confirm_date = dateutil.parser.parse(sales[number]['confirmation_date']).date()
            worksheet.write(row, 0, tools.ustr(confirm_date.strftime('%d-%m-%Y')))
            worksheet.write(row, 1, tools.ustr(sales[number].get('name')))
            worksheet.write(row, 2, tools.ustr(sales[number].get('amount_tax') or '-'))
            worksheet.write(row, 3, tools.ustr(sales[number].get('amount_untaxed') or '-'))
            worksheet.write(row, 4, tools.ustr(sales[number].get('amount_total') or '-'))
            worksheet.write(row, 5, tools.ustr(sales[number].get('amount') or '-'))

            taxes = sales[number].get('amount_tax') or 0.0
            paid = sales[number].get('amount_untaxed') or 0.0
            total_amount = sales[number].get('amount_total') or 0.0
            credit_amount = sales[number].get('amount') or 0.0

            tax = tax + taxes
            due = due + paid
            total = total + total_amount
            credit = credit + credit_amount
            row+=1

        worksheet.write(row+2, 1, tools.ustr('Total'),style1)
        worksheet.write(row+2, 2, tools.ustr((round(tax,2))),style1)
        worksheet.write(row+2, 3, tools.ustr((round(due,2))),style1)
        worksheet.write(row+2, 4, tools.ustr((round(total,2))),style1)
        worksheet.write(row+2, 5, tools.ustr((round(credit,2))),style1)
        worksheet.write(row+4, 4, tools.ustr('Balance'),style1)
        worksheet.write(row+4, 5, tools.ustr((round(total-credit,2))),style1)

        first=worksheet.merge(0,0,2,3)

            
        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['sale.order.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'sale.order.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return True

class sale_order_excel(models.TransientModel):
    _name= "sale.order.excel"
    _description = "Sales Order Excel Report"

    excel_file = fields.Binary('Excel Report for Sale Order')
    file_name = fields.Char('Excel File', size=64)

