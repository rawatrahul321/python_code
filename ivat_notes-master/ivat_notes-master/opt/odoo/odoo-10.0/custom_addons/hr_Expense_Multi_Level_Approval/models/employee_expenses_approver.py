#-*- coding:utf-8 -*-

from odoo import models, fields

class EmployeeExpensesApprover(models.Model):
    _name = "hr.employee.expenses.approver"
    _order= "sequence"
    
    employee = fields.Many2one('hr.employee', string='Employee', required=True)
    approver = fields.Many2one('hr.employee', string='Approver', required=True)
    sequence = fields.Integer(string='Approver Sequence', default=10, required=True)
    