# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class Attendance(models.Model):
    
    _inherit = 'hr.attendance'

    machine_id = fields.Char(string="Stage/Machine ID")
    check_in = fields.Datetime(string="Check In", default=False, required=False)


    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """Override the validations to receive any kind of data
        """
        pass

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """Override the validations to receive any kind of data
        """
        pass
    
    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        """Override the validations to receive any kind of data
        """
        pass

    @api.multi
    def name_get(self):
        result = []
        for attendance in self:
            if not attendance.check_out:
                result.append((attendance.id, _("Attendance for %(empl_name)s") % {
                    'empl_name': attendance.employee_id.name_related,
                }))
            else:
                result.append((attendance.id, _("Attendance for %(empl_name)s ") % {
                    'empl_name': attendance.employee_id.name_related,                   
                }))
        return result



class Employee(models.Model):
    
    _inherit = 'hr.employee'

    employee_ref = fields.Char('Employee ID', help='Employee Id Of Employee.')
