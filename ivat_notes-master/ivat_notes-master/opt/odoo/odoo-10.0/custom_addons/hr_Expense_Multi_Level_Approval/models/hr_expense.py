#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrExpense(models.Model):
    _inherit = "hr.expense"
    
    @api.onchange('employee_id')
    def onchange_field(self):
        if self.employee_id :
            self.department_id = self.employee_id.department_id
    
    department_id = fields.Many2one('hr.department',string = 'Department',compute = 'onchange_field')

class HrExpenseSheet(models.Model):

    _name = "hr.expense.sheet"
    _inherit = "hr.expense.sheet"
    
    def _default_employee(self):
        print 'Employee Id+++',self.env.context.get('default_employee_id') 
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    
    def _default_approver(self):
        employee = self._default_employee()
        eid = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        print 'EID+++',eid
        if eid.expenses_approvers:
                return eid.expenses_approvers[0].approver.id
    
    pending_approver = fields.Many2one('hr.employee', string="Pending Approver", readonly=True, default=_default_approver)
    pending_approver_user = fields.Many2one('res.users', string='Pending Approver User', related='pending_approver.user_id', related_sudo=True, store=True, readonly=True)
    current_user_is_approver = fields.Boolean(string= 'Current User is Approver', compute='_compute_current_user_is_approver')
    approbations = fields.One2many('hr.employee.expenses.approbation', 'expenses', string='Approvals')
    pending_transfered_approver_user = fields.Many2one('res.users', string='Pending Transfered Approver User', compute="_compute_pending_transfered_approver_user", search='_search_pending_transfered_approver_user')
    notes = fields.Char('Notes')
    department_id = fields.Many2one('hr.department',string = 'Department') 
#     state = fields.Selection([('submit', 'Submitted'),
#                               ('to_approve','To Approve'),
#                               ('approve', 'Approved'),
#                               ('post', 'Posted'),
#                               ('done', 'Paid'),
#                               ('cancel', 'Refused')
#                               ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False, default='submit', required=True,
#         help='Expense Report State')
    
    @api.multi
    def action_confirm(self):
        super(HrExpenseSheet, self).action_confirm()
        for expense in self:
            if expense.employee_id.expenses_approvers:
                expense.pending_approver = expense.employee_id.expenses_approvers[0].approver.id
    
    @api.multi
    def action_approve(self):
        for expense in self:
            is_last_approbation = False
            sequence = 0
            next_approver = None
            for approver in expense.employee_id.expenses_approvers:
                sequence = sequence + 1
                if expense.pending_approver.id == approver.approver.id:
                    if sequence == len(expense.employee_id.expenses_approvers):
                        is_last_approbation = True
                    else:
                        next_approver = expense.employee_id.expenses_approvers[sequence].approver
            if is_last_approbation:
                expense.action_validate()
            else:
                exp = self.env['hr.expense'].search([('sheet_id','=',self.id)],limit = 1)
                expense.write({'state': 'submit', 'pending_approver': next_approver.id})
                print 'HELLO SUBMIT+++++++++++'
                e = self.env['hr.expense'].search([('sheet_id','=',self.id)],limit=1)
                a = e.id
                b = self.env.uid
                c = sequence
                d = fields.Datetime.now()
#                 self.env.cr.execute("insert into hr_employee_expenses_approbation (expenses,approver,sequence,date) values (%s,%s,%s,%s)",(a,b,c,d))
                self.env['hr.employee.expenses.approbation'].create({'expenses': expense.id, 'approver': self.env.uid, 'sequence': sequence, 'date': fields.Datetime.now()})
            
    @api.multi
    def action_validate(self):
        self.write({'pending_approver': None})
        for expense in self:
            e = self.env['hr.expense'].search([('sheet_id','=',self.id)],limit=1)
            self.env['hr.employee.expenses.approbation'].create({'expenses': expense.id, 'approver': self.env.uid, 'date': fields.Datetime.now()})
        super(HrExpenseSheet, self).approve_expense_sheets()
    
    @api.one
    def _compute_current_user_is_approver(self):
        if self.pending_approver.user_id.id == self.env.user.id or self.pending_approver.transfer_expenses_approvals_to_user.id == self.env.user.id :
            self.current_user_is_approver = True
        else:
            self.current_user_is_approver = False
    
    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id and self.employee_id.expenses_approvers:
            self.pending_approver = self.employee_id.expenses_approvers[0].approver.id
        else:
            self.pending_approver = False
            
    @api.one
    def _compute_pending_transfered_approver_user(self):
        self.pending_transfered_approver_user = self.pending_approver.transfer_expenses_approvals_to_user
    
    def _search_pending_transfered_approver_user(self, operator, value):
        replaced_employees = self.env['hr.employee'].search([('transfer_expenses_approvals_to_user', operator, value)])
        employees_ids = []
        for employee in replaced_employees:
            employees_ids.append(employee.id)
        return [('pending_approver', 'in', employees_ids)]


# class Uninstall(models.Model):
#     
#     _inherit = 'base.module.upgrade'
#  
#     def upgrade_module(self, cr, uid, ids, context=None):
#         
#         
#         res = super(Uninstall, self).upgrade_module(cr, uid, ids, context=context)
#         ir_module  = self.pool.get('ir.module.module')
#         
#         followers  = self.pool.get('mail.followers')
#         
#         followers_ids = followers.search(cr, uid, [('res_model', 'in', ['hr.expense.sheet'])]) 
#         ids = ir_module.search(cr,
#         
#         uid, [('state', 'in', ['to remove'])])
#         
#         for j in ir_module.browse(cr, uid, ids):
#         
#             if j.name == 'hr_Expense_Multi_Level_Approval':
#         
#                 for i in followers.browse(cr, uid, followers_ids): i.unlink()
#         return res






    
    