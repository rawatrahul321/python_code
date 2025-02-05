from odoo import api, fields, models, _
from datetime import datetime, timedelta



class hr_contract(models.Model):
    _inherit = 'hr.contract'

    is_hourly_pay = fields.Boolean(string='Hourly Pay')


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'
    
    @api.multi
    @api.depends('date_to', 'date_from', 'employee_id')
    def _compute_employee_total_hours(self):
        for payslip in self:
            total_days = 0
            att_ids = self.env['hr.attendance'].search([('employee_id', '=', payslip.employee_id.id),
                                            ('check_out', '>=', datetime.strptime(payslip.date_from, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')),
                                            ('check_out', '<=', datetime.strptime(payslip.date_to, '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')),])
            for rec in payslip.worked_days_line_ids:
                if rec.name == 'Normal Working Days paid at 100%':
                    total_days += rec.number_of_days
                    payslip.normal_hrs += rec.number_of_hours
                    print 'Total Days++++++++++++',total_days
            if att_ids:
                total_seconds = 0;
                for att in att_ids:
                    record_time = str(timedelta(hours=att.worked_hours)).split(':')
                    if record_time and len(record_time) >= 2:
                        conv_time = datetime.strptime(record_time[0] + ':' + record_time[1], '%H:%M')
                        if conv_time:
                            total_seconds += conv_time.minute * 60 + conv_time.hour * 3600
                day = total_seconds // 86400
                hour = (total_seconds - (day * 86400)) // 3600
                minute = (total_seconds - ((day * 86400) + (hour * 3600))) // 60
                temp = str(hour + (24 * day)) + ':' + str(minute)
#                 print 'TEMP++++++++',temp
                payslip.total_hours = int(temp.split(':')[0]) - total_days
                print '+++Payslips Total Hours +++++++++++',payslip.total_hours 
                
    total_hours = fields.Float(string="Employee Total Working Hours", compute='_compute_employee_total_hours',store=True,default=False)
    normal_hrs = fields.Float(string="Normal Working Hours",compute='_compute_employee_total_hours',store=True,default=False)

