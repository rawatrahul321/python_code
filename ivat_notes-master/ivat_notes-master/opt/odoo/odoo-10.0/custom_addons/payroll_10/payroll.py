from openerp import api, fields, models, _
from datetime import date, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime 
import time
import odoo.addons.decimal_precision as dp

class hr_employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
        
    @api.multi
    @api.depends('name','emp_code')
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            emp_code = record.emp_code
            if record.emp_code:
                name =  "[%s] %s" % (emp_code ,name)
            else:
                name =  "%s" % (name)
            result.append((record.id, name))
        return result
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('emp_code', operator, name)]
        pos = self.search(domain + args, limit=limit)
        return pos.name_get() 
    
    @api.onchange('birthday')
    def onchange_dob(self):
        if self.birthday:
            print 'Date of Birth :- @@@@@' ,self.birthday  ,datetime.today()     
            birthday= datetime.strptime(self.birthday, '%Y-%m-%d')
            age= ((datetime.today() - birthday).days/365)
            self.age = age
    
    @api.one
    def get_time(self):
        users = self.env['res.users.log'].search([('create_uid','=',self.user_id.id)])[0]
        print '***USERS****',users
        self.login_date = users.write_date
        
    pf_no = fields.Char('PF Number')
    pf_org = fields.Char('PF Organization')
    pen_acc_no = fields.Char('Pension Account Number')
    esi_acc_no = fields.Char('ESI Account Number')
    insurance = fields.Char('Insurance')
    date_of_joining = fields.Date('Date Of Joining',default=fields.datetime.now())
    father_name = fields.Char("""Father's Name""")
    qualification = fields.Char('Qualification')
    family_detail = fields.Char('Family Details')
    emp_code = fields.Char('Employee Code')
    organ_name = fields.Many2one('res.partner','Organization Name')
    division = fields.Many2one('hr.division','Division')
    date_of_confirm = fields.Date('Date Of Confirmation')
    sub_dept = fields.Many2one('hr.department','Sub Department')
    grade = fields.Many2one('hr.grade','Grade')
    age = fields.Float('Age')
    passport_no = fields.Char('Passport Number')
    passport_expiry = fields.Date('Passport Expiry')
    email = fields.Char('Email Id')
    exp_detail = fields.Char('Experience Detail')
    blood_group = fields.Char('Blood Group')
    basic = fields.Float('Basic')
    hra = fields.Float('House Rent Allowance')
    conveyance = fields.Float('Conveyance Allowance')
    exec_alw = fields.Float('Executive Allowance')
    oth_alw = fields.Float('Other Allowance')
    resig = fields.Date('Resignation Date')
    terminate = fields.Date('Termination Date')
    retire_date = fields.Date('Retirement Date')
    full_final  = fields.Integer('Full & Final Settlement')
    boss = fields.Boolean('Boss')
    boss_number = fields.Char('Boss Mobile Number')
    boss_secretary = fields.Char('Boss Secretary', help = "Boss Secretary Contact Number")
    
    login_date = fields.Datetime('Latest connection',compute='get_time',store=True,default=False)  
    company_id = fields.Many2one('res.company', string='Company',store=True, 
    required=True,default=lambda self: self.env['res.company']._company_default_get('hr.employee'))
    
    active = fields.Boolean('Active', default=True)
    
    
    
class HrGrade(models.Model):
    _name = 'hr.grade'
    _description = "HR Grade"
    
    name = fields.Char('Grade Name')    

class HrDivision(models.Model):
    _name = 'hr.division'
    _description = "HR Division"
    
    name = fields.Char('Division Name')    

    
class hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'
    
    @api.onchange('struct_id')
    def onchange_increment_date(self):
        if self.struct_id:
            self.date_start = self.employee_id.date_of_joining
    
    basic = fields.Float('Basic')
    hra = fields.Float('House Rent Allowance')
    conveyance = fields.Float('Conveyance Allowance')
    exec_alw = fields.Float('Executive Allowance')
    oth_alw = fields.Float('Other Allowance')
    working_hours = fields.Many2one('resource.calendar', string='Working Schedule',required=True)
    
    

