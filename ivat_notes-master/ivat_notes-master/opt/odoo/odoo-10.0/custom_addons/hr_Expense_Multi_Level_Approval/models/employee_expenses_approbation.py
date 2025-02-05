#-*- coding:utf-8 -*-

from odoo import models, fields

class EmployeeExpensesApprobation(models.Model):
    _name = "hr.employee.expenses.approbation"
    _order= "sequence"
    
    expenses = fields.Many2one('hr.expense.sheet', string='Expenses', required=True)
    approver = fields.Many2one('res.users', string='Approver', required=True)
    sequence = fields.Integer(string='Approbation Sequence', default=10, required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now())
    