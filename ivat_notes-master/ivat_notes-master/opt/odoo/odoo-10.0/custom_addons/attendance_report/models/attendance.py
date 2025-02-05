from odoo import models, fields, api, _, exceptions

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
class Holidays(models.Model):
    _inherit = 'hr.holidays'

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    total_attendance = fields.Integer('Attendance',compute='get_attendance')
    total_leave = fields.Integer('Leaves',compute='get_leave')
    
    @api.one
    def get_attendance(self):
        print '++++ENTRY++++',self.user_id.id
#         attendance = self.env['hr.attendance'].search_count([('employee_id','=',self.id)])
        a = self.env.cr.execute("SELECT date_trunc('month', CURRENT_DATE)::timestamp;")
        first_date = self.env.cr.fetchall()[0][0]
        b = self.env.cr.execute("SELECT date_trunc('month', CURRENT_DATE)::timestamp + interval '1 month - 1 day';")
        last_date = self.env.cr.fetchall()[0][0]
        print 'First And Last Date++',first_date,   last_date
        emp_attendance = self.env['hr.attendance'].search_count([('employee_id', '=', self.id),('check_in', '>=', first_date),('check_out', '<=', last_date)])                     
        print '++++Attendance++++',emp_attendance
        self.total_attendance = emp_attendance

    @api.one
    def get_leave(self):
        leave = self.env['hr.holidays'].search_count([('employee_id','=',self.id)])
        print '** Leave **',leave
        self.total_leave = leave

