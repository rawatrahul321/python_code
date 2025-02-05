from odoo import models, fields, api
from odoo.tools.translate import _

import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError
import time
from dateutil import relativedelta
from openerp.report import report_sxw
from datetime import datetime
# from odoo.osv import osv




class tax_and_savings(models.Model):
    _name ='tax.and.savings'
    
    name=fields.Char('Savings Category')
    catagory_limit=fields.Float('Limit')
    

class hr_contract(models.Model):
    _inherit="hr.contract"
    
    notds=fields.Char('No Tds')
    
class saving_type(models.Model):
    _name ='saving.type'    
    
    name=fields.Char('Saving Type')
    savings=fields.Many2one('tax.and.savings','Savings Category')
    

class tax_slabs(models.Model):
    _name ='tax.slabs'
    
    
#     def tax_slab(self):
#         self.name="Tax Slab" 
    
    name=fields.Char('Name')
    percent = fields.Float('Percentge of Deduction')
    from_limit = fields.Float('Start Limit')
    to_limit = fields.Float('To Limit')

class employee_saving(models.Model):
    _name = 'employee.saving'
    
#     @api.one
#     @api.onchange('employee_id')
#     def onchange_employee_id(self):
#         employee = self.env['employee.saving'].search([('employee_id', '=', self.employee_id.id)])
#         if employee:
# #             print '===============',self.employee_id
# 
# #             self.employee_id=False
# #             print '===============',self.employee_id
# 
#             raise ValidationError(_('Employee saving record already exists! Please update the existing record.'))
#         return True
 
    @api.one
    @api.depends('saving_line_ids.amount')
    def get_amount(self):
         
        for each in self:
            total =0.0
            for line in self.saving_line_ids:
                total += line.amount
            each.proposed_amount = total    
        return True 
    
    @api.one
    @api.depends('medical_line_ids.amount')
    def get_amount_receipt(self):
         
        
        for each in self:
            total =0.0
            for line in self.medical_line_ids:
                total += line.amount
            each.bill_amount = total    
        return True 
    
    @api.one
    @api.depends('hra_line_ids.amount')
    def get_amount_receipt_hra(self):
         
        for each in self:
            total =0.0
            for line in self.hra_line_ids:
                total += line.amount
            each.hra_receipt_amount = total    
        return True 
    
    @api.one
    @api.depends('other_income_ids.amount')
    def get_amount_other(self):
         
        for each in self:
            total =0.0
            for line in self.other_income_ids:
                total += line.amount
            each.other_income_amount = total    
        return True 
    
#     @api.depends('employee_id')
#     def get_name(self):
#         self.name=self.employee_id.name_related
    
    name =fields.Char('Name')
    employee_id = fields.Many2one('hr.employee', string = 'Employee Name',required = True)
    fin_year_id=fields.Many2one('account.fiscalyear','Financial Year')
    proposed_amount=fields.Float(string='Saving Amount',digits_compute=dp.get_precision('Account'),compute='get_amount', store=True,default=False)
    saving_line_ids =fields.One2many('saving.line','saving_id','Saving Line')
    medical_line_ids =fields.One2many('medical.bill.line','bill_id','Medical Bill')
    hra_line_ids =fields.One2many('hra.receipt.line','hra_receipt_id','HRA Receipt')
    other_income_ids=fields.One2many('other.source.income','income_id','Other Income')                                                    
    bill_amount=fields.Float(string='Medical Bill Amount',digits_compute=dp.get_precision('Account'),compute='get_amount_receipt', store=True,default=False)
    hra_receipt_amount=fields.Float(string='HRA Receipt Amount',type='float',digits_compute=dp.get_precision('Account'),compute='get_amount_receipt_hra',store=True,default=False)
    other_income_amount=fields.Float(string='Other Source Amount',type='float',digits_compute=dp.get_precision('Account'),compute='get_amount_other',store=True,default=False)

    gross_income_previous=fields.Float('Gross Income')
    professional_tax_previous=fields.Float('Professional Tax')
    ded_previous_emp=fields.Float('Deduction Made By Previous Employer')
    income_tax_paid=fields.Float('Income Tax Paid')
    car_perks=fields.Float('Car Perks')
    lease_perks=fields.Float('Lease Perks')
    hard_furnishing_perks=fields.Float('Hard Furnishing Perks')
    other_perks=fields.Float('Other Perks')
    entertainment_allowance=fields.Float('Entertainment Allowance')
    lease_exemption=fields.Float('Lease Exemption')
    furniture_rent_recovery=fields.Float('Furniture Rent Recovery')
    actual_lease_rent_paid=fields.Float('Actual Lease Rent Paid')
    furnishing_allowance=fields.Float('Furnishing Allowance')
    conveyance_recovery=fields.Float('Trans Monthly Exempt')
    date = fields.Date('Date',default=datetime.now())
    
    medical_exp_reimbursement=fields.Float('Medical Expense Reimbursement')
    prp_amount=fields.Float('PRP Amount')
    preconstruction_interest=fields.Float('Preconstruction Interest')
    prof_updation_exempt=fields.Float('Professional Updation Exempt')
    uniform_fitment_exempt=fields.Float('Uniform Fitment Exempt')
    property_type=fields.Selection([('S','Self Occupied'),('R','Rent Out')],"Property Type")
    house_income_sl =fields.Float('HP Income (Self Lease)',readonly=True)
    uniform_amount=fields.Float('Uniform Fitment Amount')
                
                
    
    
class saving_line(models.Model):
    _name = 'saving.line'
    
    
    name=fields.Char('Name')
    saving_id=fields.Many2one('employee.saving','Saving Id')
    salary_rule_id=fields.Many2one('saving.type','Saving Name')
    type= fields.Selection([('P', 'Proposed'),('C', 'Confirmed')], "Saving Type")
    prop_type= fields.Selection([('S', 'Self Occupied'),('R', 'Rented Out')], "Property Type")
    amount=fields.Float('Amount')
    saving_no=fields.Char('Saving Number')
                
class medical_bill_line(models.Model):
    _name = 'medical.bill.line'
    
    
    name=fields.Char('Name')
    bill_num=fields.Char('Bill Number')
    bill_id=fields.Many2one('employee.saving','Bill Id')
    amount=fields.Float('Amount')
    date=fields.Date('Date')
    type= fields.Selection([('P', 'Proposed'),('C', 'Confirmed')], "Type")
    reference=fields.Char('Reference')
    
               
class hra_receipt_line(models.Model):
    _name = 'hra.receipt.line'
    
    
    name=fields.Char('Name')
    hra_receipt_id=fields.Many2one('employee.saving','HRA Receipt Id')
    amount=fields.Float('Amount')
    date=fields.Date('Date')
    type= fields.Selection([('P', 'Proposed'),('C', 'Confirmed')], "Type")
    reference=fields.Char('Reference')
    
    
class other_source_income(models.Model):
    _name = 'other.source.income'
    
    
    name = fields.Char('Name')
    income_source = fields.Selection([('1','Income From House Property'),('2','Interest On FD'),('4','Saving Interest Income'),('3','Other')],'Income Source',required='True')
    income_id = fields.Many2one('employee.saving','Income Id')
    amount = fields.Float('Amount')
    date = fields.Date('Date')
    reference = fields.Char('Reference')
    
class employee__internal_saving(models.Model):
    _name = 'employee.internal.saving'
    
  
    name =fields.Char('Name')
    employee_id =fields.Many2one('hr.employee','Employee Name')
    salary_rule_id = fields.Many2one('saving.type','Saving Name')
    amount = fields.Float('Amount')
    saving_no = fields.Char('Saving Number')
    date_to = fields.Date('End Date')
    date = fields.Date('Date')
                
   

class pay_image(models.Model):   
    _name='pay.image'
    
    employee_id=fields.Integer("Employee Id")
    pay_code=fields.Char("Code")
    amount=fields.Float("Amount")
    yymm=fields.Integer("YYMM")
    fin_year=fields.Integer("Financial Year")




class hr_payslip_inherit(models.Model):
    _inherit = 'hr.payslip'
    
    fin_year=fields.Many2one('account.fiscalyear', 'Financial Year',readonly=True,states={'draft': [('readonly', False)]})
    tds_id = fields.Many2one('employee.tds','Tax Reference',readonly=True,states={'draft': [('readonly', False)]})

    @api.multi
    def compute_sheet(self):
        print 'HRPAYSLIP COMPUTE SHEET'  
        
            
#         for emp_slip in self.env['hr.payslip'].search([]):
#                    
#                 print 'sdlks;lkasjgamkl.jmdglkasjmdg',emp_slip.name
#                    
#                 if emp_slip.name==self.name and emp_slip.state=='done':
#                     raise ValidationError(_('Employee payslip already present for the current month'))
#                      
#                     print '=================================',emp_slip
#  
#                 else:
#                     print '=================================',emp_slip
 
        for payslip in self:
            access=0
#             global employee 
            
            print '@@@@@@@@@@@@@@@@@@@',payslip.journal_id
            
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            #delete old payslip lines
            payslip.line_ids.unlink()
            print 'payslip.line_ids',payslip.line_ids
            payslip.details_by_salary_rule_category.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines = [(0, 0, line) for line in self.get_payslip_lines(contract_ids, payslip.id)]
            
            
            payslip.write({'line_ids': lines, 'number': number})


#================================= INCOME TAX COMPUTATION =======================            

            for slip in self.env['hr.payslip'].search([('number', '=',number )]):
#                 print'+++++++++++++++++++++++++++', slip.employee_id
                employee=slip.employee_id.id
                  
                slip_id=slip.id
                  
#                 if not slip.line_ids:
#                     raise ValidationError(_('Please Compute Sheet First'))
#                 else:
#                     access=1
                 
                 
#         if access==1:
            for slips in self.env['hr.payslip'].search([('number', '=', number)]):
                 
                emp=slips.employee_id.id
#                 print 'EEEEEEEEMMMMMMMMMPPPPPPP',emp
                tax_sheet='Income Tax for '+slips.employee_id.name_related
                fin_year=slips.fin_year.id
                print 'finyearrrrrrrrr',fin_year
                date_frm=slips.date_from
                print 'slip datefrom',date_frm
                date_to=slips.date_to
                sl=slips.id
                print 'slip id',sl
                
         
        #===============Taxation Variables ==================
#                 dat=self.date_from
#                 print'self date from',dat
                date =datetime.strptime(date_frm, "%Y-%m-%d")
                month=date.month
                term=15
                ded_80c_limit=150000
                exmp_80c=0
                total_tax_income=0
                ded_80_c=0
                net_exemption=0
                deduction_12_mnth=0
                deduction_curr_mnth=0
                deduction_curr_mnth_ps=0
                deduction_12_mnth_cess=0
                
#================ Saving Catagories ===================
 
                total_saving_80c=0
                limit_80c=0
                 
                total_saving_80cccd_1b=0
                limit_80cccd_1b=0
                 
                total_saving_24=0
                limit_24=0
                 
                total_saving_80e=0
                limit_80e=0
                 
                total_saving_80ccg=0
                limit_80ccg=0
                 
                total_saving_80d_parents=0
                limit_80d_parents=0
                 
                total_saving_80d_self=0
                limit_80d_self=0
                 
                total_saving_80ddb=0
                limit_80ddb=0
                 
                total_saving_80u=0
                limit_80u=0
                 
                total_saving_80dd=0
                limit_80dd=0
                 
                total_saving_80g=0
                limit_80g=0
                 
                total_saving_80ggc=0
                limit_80ggc=0
                 
                total_saving_80tta=0
                limit_80tta=0
 
 
#=============== Basic Pay ==========================
                basic=0
                actual_basic=0
                gross_basic=0
                net_basic=0
                proj_basic=0
                exmp_basic=0
             
#=============== Dearness Alw ==========================
                da=0
                actual_da=0
                gross_da=0
                net_da=0
                proj_da=0
                exmp_da=0
                 
#=============== Transport Alw ==========================
                tca=0
                actual_tca=0
                gross_tca=0
                net_tca=0
                proj_tca=0
                exmp_tca=19200  
                 
#=============== House Rent Alw ==========================
                
                hra=0
                actual_hra=0
                gross_hra=0
                net_hra=0
                proj_hra=0
                exmp_hra=0    
                 
#=============== Other Alw ==========================
                  
                spa=0
                actual_spa=0
                gross_spa=0
                net_spa=0
                proj_spa=0
                exmp_spa=0 
                 
#=============== Scholarship Alw ==========================
                sch=0
                actual_sch=0
                gross_sch=0
                net_sch=0
                proj_sch=0
                exmp_sch=0 
                 
#=============== Medical Alw ==========================
                med=0
                actual_med=0
                gross_med=0
                net_med=0
                proj_med=0
                exmp_med=0 
                 
#=============== Provident Fund ==========================
                 
                pf=0
                actual_pf=0
                proj_pf=0
                net_pf=0
                 
#============== Saving Data =============================
                 
                saving=0
                hra_saving=0
                medical_saving=0
                other_income=0
                hra_deductions=0
                
 
#================ Calculate Totals =======================  
                 
                total_gross=0
                total_exmp=0
                total_net=0
                
                
#================ Tax Variables ============================
               
                slab1_fromlimit=0
                slab1_tolimit=0
                slab1_percent=0
               
                slab2_fromlimit=0
                slab2_tolimit=0
                slab2_percent=0
               
                slab3_fromlimit=0
                slab3_tolimit=0
                slab3_percent=0
                
                slab4_fromlimit=0
                slab4_tolimit=0
                slab4_percent=0
                
                actual_tds=0
                
               
                
 
 
#                 print'beeeeeeforrrreeee'
                 
                a = self.env['employee.tds'].search([('employee_id','=',emp),('date_from','=',date_frm),('date_to','=',date_to)])
#                 print'kkkkkkkkkkksssssssssssssssskkkkkk' ,a
     
                       
                if a:
           
                    self.env.cr.execute("update employee_tds set employee_id=%s,fin_year_id=%s where date_from=%s and date_to=%s and employee_id=%s ;",(emp,fin_year,date_frm,date_to,emp))
                else:
                    self.env.cr.execute("insert into employee_tds (employee_id,fin_year_id,date_from,date_to,name) values(%s,%s,%s,%s,%s);",(emp,fin_year,date_frm,date_to,tax_sheet))
                 
                b = self.env['employee.tds'].search([('employee_id','=',emp),('date_from','=',date_frm),('date_to','=',date_to)])
     
                slips.tds_id=b.id
                 
                emp_tds_id = b.id 
                 
#                 print 'employee_tds_id=========',emp_tds_id
                 
#                 print '=================+SLIP==========================+==',sl
                 
#============================== Current payslip Data =============================
 
                self.env.cr.execute("select code,total from hr_payslip_line where slip_id=%s;",(sl,))
                proj = self.env.cr.dictfetchall()
                 
#============================== PayImage Data =============================
 
                self.env.cr.execute("select pay_code,employee_id,yymm,amount from pay_image where employee_id=%s and yymm >201803 and yymm<201903;",(employee,))
                actual= self.env.cr.dictfetchall()
 
#============================== Saving Data =============================
 
                self.env.cr.execute("""select coalesce(proposed_amount,0) as saving,coalesce(bill_amount,0) as medical,coalesce(hra_receipt_amount,0) as hra,coalesce(other_income_amount,0) as other from employee_saving where employee_id=%s;""",(employee,))
                saving = self.env.cr.dictfetchall()
                 
                print 'INCOME FROM OTHER SOURCE+++++++++',saving
                 
                for k in saving:
                    saving=k['saving']
                    medical_saving=k['medical']
                    hra_saving=k['hra']
                    other_income=k['other']
                     
                                     
#                 print 'HRA Saving Reciepts = ',hra_saving
#                 print 'Savings From Savings Form = ',saving
#                 print 'MEDICAL = ',medical_saving
                    print 'OTHER savings = ',other_income
 
 
 
 
 
#=======================Projection Data ===============================                
                for i in proj:
                    if i['code'] =='BASIC' :
                        basic=i['total']
                    if i['code'] =='HRAMN' :
                        hra=i['total']
                    if i['code'] =='TCA' :
                        tca=i['total']
                    if i['code'] =='DA' :
                        da=i['total']
                    if i['code'] =='EPMF' :
                        pf=-(i['total'])
                    if i['code'] =='SCH' :
                        sch=i['total']
                    if i['code'] =='SPA' :
                        spa=i['total']
                    if i['code'] =='MEDA' :
                        med=i['total']
                     
                     
#                 print 'BASIC =',basic
#                 print 'DA =',da
#                 print 'HRA =',hra
#                 print 'TCA = ',tca
#                 print 'PF = ',pf
#                 print 'SCA = ',spa
#                 print 'SCH =',sch
#                 print 'MED =',med
#                 print 'Which Month ? ---> ',month
                         
# ================= PROJECTION CALCULATION ============================                
                if month<4 and month !=0:
                    month=month+12
                     
                print 'projected_term',term-month+1
#================= Projected Salary Heads ========================                
                proj_basic = basic*((term-month)+1)
                proj_hra = hra*((term-month)+1)
                proj_da = da*((term-month)+1)
                proj_tca = tca*((term-month)+1)
                proj_pf = pf*((term-month)+1)
                proj_sch=sch*((term-month)+1)
                proj_spa=spa*((term-month)+1)
                proj_med=med*((term-month)+1)
                 
                 
#========================= DATA FROM PAYIMAGE ========================================                                     
                for i in actual:
                    
                    if i['pay_code'] =='BASIC' :
                        actual_basic=actual_basic + (i['amount'])
                    if i['pay_code'] =='HRAMN' :
                        actual_hra=actual_hra + (i['amount'])
                    if i['pay_code'] =='TCA' :
                        actual_tca=actual_tca + (i['amount'])
                    if i['pay_code'] =='DA' :
                        actual_da=actual_da + (i['amount'])
                    if i['pay_code'] =='EPMF' :
                        actual_pf=actual_pf + (-(i['amount']))
                    if i['pay_code'] =='SCH' :
                        actual_sch=actual_sch + (i['amount'])
                    if i['pay_code'] =='SPA' :
                        actual_spa=actual_spa + (i['amount'])
                    if i['pay_code'] =='MEDA' :
                        actual_med=actual_med + (i['amount'])
                    if i['pay_code'] =='TDS' :
                        actual_tds=actual_tds + (-(i['amount']))
                    
                    
                    
                
                 
#                 print 'ACTUAL_BASIC = ',actual_basic
#                 print 'ACTUAL_DA = ',actual_da
#                 print 'ACTUAL_HRA = ',actual_hra
#                 print 'ACTUAL_TCA = ',actual_tca
#                 print 'ACTUAL_PF = ',actual_pf
#                 print 'ACTUAL_SPA = ',actual_spa
#                 print 'ACTUAL_SCH = ',actual_sch
#                 print 'ACTUAL_MEDICAL = ',actual_med               
                 
                 
                 
                gross_basic   = proj_basic+actual_basic
                gross_hra     = proj_hra+actual_hra
                gross_da      = proj_da+actual_da
                gross_tca     = proj_tca+actual_tca
                gross_pf      = proj_pf+actual_pf
                gross_spa     =proj_spa+actual_spa
                gross_sch     =proj_sch+actual_sch
                gross_med     =proj_med+actual_med
                 
                 
                 
#                 print 'gross_Basic = ',gross_basic
#                 print 'gross_hra = ',gross_hra
#                 print 'gross_da = ',gross_da
#                 print 'gross_tca = ',gross_tca
#                 print 'gross_pf = ',gross_pf
#                 print 'gross_sch = ',gross_sch
#                 print 'gross_spa = ',gross_spa   
#                 print 'gross_med = ',gross_med       
                 
                 
#==================================================================                
     
                 
#                 print 'projected_basic =',proj_basic 
#                 print 'projected_hra = ',proj_hra 
#                 print 'projected_da',proj_da 
#                 print 'projected_tca',proj_tca 
#                 print 'projected_pf',proj_pf 
#                 print 'projected_sch', proj_sch
#                 print 'projected_spa', proj_spa
#                 print 'projected_med', proj_med
                 
#==================================================================                
                 
                 
#======================== Exemption Calculation ==========================================               
                 
                if gross_tca<exmp_tca:
                    exmp_tca=gross_tca
                else:    
                    exmp_tca=gross_tca-exmp_tca
                 
                 
                if medical_saving>gross_med:
                    exmp_med=gross_med
                else:    
                    exmp_med=medical_saving
                 
                if ded_80c_limit>gross_pf:
                    exmp_80c=gross_pf
                else:
                    exmp_80c=ded_80c_limit
 
#========================== Net Salary Calculation=================================
 
                
                net_basic   = gross_basic-exmp_basic
                net_hra     = gross_hra-exmp_hra
                net_da      = gross_da=exmp_da
                net_tca     = gross_tca-exmp_tca
                net_pf      = net_pf-exmp_80c
                net_spa     = gross_spa-exmp_spa
                net_sch     = gross_sch-exmp_sch
                net_med     = gross_med-exmp_med
                 
                 
                 
#                 print 'net_Basic = ',net_basic
#                 print 'net_hra = ',net_hra
#                 print 'net_da = ',net_da
#                 print 'net_tca = ',net_tca
#                 print 'net_pf = ',net_pf
#                 print 'net_sch = ',net_sch
#                 print 'net_spa = ',net_spa   
#                 print 'net_med = ',net_med      
#                  
 
 
 
# =================== EMPLOYEE SAVING LINE ======================      
           
                self.env.cr.execute("""select ts.name as catagory,ts.catagory_limit,st.name,sl.amount,es.employee_id from tax_and_savings ts left join saving_type st on st.savings=ts.id 
                            left join saving_line sl on sl.salary_rule_id=st.id left join employee_saving es on es.id=sl.saving_id where es.employee_id=%s;""",(employee,))
                saving_lines = self.env.cr.dictfetchall()
                 
#                 print '====================',saving_lines
                 
                self.env.cr.execute('select name,catagory_limit from tax_and_savings;')
                 
                catagory_limit=self.env.cr.dictfetchall()
#                 print '====================',catagory_limit
 
                 
                for limit in catagory_limit:
                    if limit['name']=='80C/80CCC/80CCD':
                        limit_80c=limit['catagory_limit']
                         
                         
                    if limit['name']=="80CCD(1B)":
                        limit_80cccd_1b=limit['catagory_limit']
                         
                       
                         
                    if limit['name']=="24":
                        limit_24=limit['catagory_limit']
                        
                         
                    if limit['name']=="80E":
                        limit_80e=limit['catagory_limit']
                         
                         
                    if limit['name']=="80CCG":
                        limit_80ccg=limit['catagory_limit']
                         
                         
                    if limit['name']=="80D(self)":
                        limit_80d_self=limit['catagory_limit']
                     
                     
                    if limit['name']=="80D(parents)":
                        limit_80d_parents=limit['catagory_limit']
                        
                             
                             
                    if limit['name']=="80DDB":
                        limit_80ddb=limit['catagory_limit']
                        
                         
                    if limit['name']=="80U":
                        limit_80u=limit['catagory_limit']
                         
                         
                    if limit['name']=="80DD":
                        limit_80dd=limit['catagory_limit']
                        
                         
                    if limit['name']=="80G":
                        limit_80g=limit['catagory_limit']
                        
                         
                    if limit['name']=="80GGC":
                        limit_80ggc=limit['catagory_limit']
                        
                         
                    if limit['name']=="80TTA":
                        limit_80tta=limit['catagory_limit']
                         
                 
#                 print "Saving Lines =",saving_lines
 
                for tot in saving_lines:
                     
                    if tot['catagory']=='80C/80CCC/80CCD':
                        total_saving_80c=total_saving_80c+tot['amount']
                        limit_80c=tot['catagory_limit']
                         
                         
                    if tot['catagory']=="80CCD(1B)":
                        total_saving_80cccd_1b=total_saving_80cccd_1b+tot['amount']
                        limit_80cccd_1b=tot['catagory_limit']
                         
                        if total_saving_80cccd_1b >limit_80cccd_1b:
                            total_saving_80cccd_1b=limit_80cccd_1b
                         
                    if tot['catagory']=="24":
                        total_saving_24=total_saving_24+tot['amount']
                        limit_24=tot['catagory_limit']
                        if total_saving_24 >limit_24:
                            total_saving_24=limit_24
                         
                    if tot['catagory']=="80E":
                        total_saving_80e=total_saving_80e+tot['amount']
                        limit_80e=tot['catagory_limit']
                        if total_saving_80e>limit_80e:
                            total_saving_80e=limit_80e
                         
                    if tot['catagory']=="80CCG":
                        total_saving_80ccg=total_saving_80ccg+tot['amount']
                        limit_80ccg=tot['catagory_limit']
                        if total_saving_80ccg>limit_80ccg:
                            total_saving_80ccg=limit_80ccg
                         
                    if tot['catagory']=="80D(self)":
                        total_saving_80d_self=total_saving_80d_self+tot['amount']
                        limit_80d_self=tot['catagory_limit']
                        if total_saving_80d_self>limit_80d_self:
                            total_saving_80d_self=limit_80d_self
                     
                    if tot['catagory']=="80D(parents)":
                        total_saving_80d_parents=total_saving_80d_parents+tot['amount']
                        limit_80d_parents=tot['catagory_limit']
                        if total_saving_80d_parents>limit_80d_parents:
                            total_saving_80d_parents=limit_80d_parents
                     
                     
                             
                    if tot['catagory']=="80DDB":
                        total_saving_80ddb=total_saving_80ddb+tot['amount']
                        limit_80ddb=tot['catagory_limit']
                        if total_saving_80ddb>limit_80ddb:
                            total_saving_80ddb=limit_80ddb
                         
                    if tot['catagory']=="80U":
                        total_saving_80u=total_saving_80u+tot['amount']
                        limit_80u=tot['catagory_limit']
                        if total_saving_80u>limit_80u:
                            total_saving_80u=limit_80u
                         
                    if tot['catagory']=="80DD":
                        total_saving_80dd=total_saving_80dd+tot['amount']
                        limit_80dd=tot['catagory_limit']
                        if total_saving_80dd>limit_80dd:
                            total_saving_80dd=limit_80dd
                         
                    if tot['catagory']=="80G":
                        total_saving_80g=total_saving_80g+tot['amount']
                        limit_80g=tot['catagory_limit']
                        if total_saving_80g>limit_80g:
                            total_saving_80g=limit_80g
                         
                    if tot['catagory']=="80GGC":
                        total_saving_80ggc=total_saving_80ggc+tot['amount']
                        limit_80ggc=tot['catagory_limit']
                        if total_saving_80ggc>limit_80ggc:
                            total_saving_80ggc=limit_80ggc
                         
                    if tot['catagory']=="80TTA":
                        total_saving_80tta=total_saving_80tta+tot['amount']
                        limit_80tta=tot['catagory_limit']
                        if total_saving_80tta>limit_80tta:
                            total_saving_80tta=limit_80tta
                         
                         
                 
#                 actual_taxable=actual_basic+actual_da+actual_hra+actual_tca
 
 
#  
#                 print ""
#                 print ""
#                 print ""
#  
#                 print 'total_saving_80c',total_saving_80c
#                 print 'limit_80c',limit_80c
#                 print 'total_saving_80cccd_1b',total_saving_80cccd_1b
#                 print 'limit_80cccd_1b',limit_80cccd_1b
#                 print 'total_saving_24',total_saving_24
#                 print 'limit_24',limit_24
#                 print 'total_saving_80e',total_saving_80e
#                 print 'limit_80e',limit_80e
#                 print 'total_saving_80ccg',total_saving_80ccg
#                 print 'limit_80ccg',limit_80ccg
#                 print 'total_saving_80d',total_saving_80d_parents
#                 print 'limit_80d',limit_80d_parents
#                 print 'total_saving_80d',total_saving_80d_self
#                 print 'limit_80d',limit_80d_self
#                 print 'total_saving_80ddb',total_saving_80ddb
#                 print 'limit_80ddb',limit_80ddb
#                 print 'total_saving_80u',total_saving_80u
#                 print 'limit_80u',limit_80u
#                 print 'total_saving_80dd',total_saving_80dd
#                 print 'limit_80dd',limit_80dd
#                 print 'total_saving_80g',total_saving_80g
#                 print 'limit_80g',limit_80g
#                 print 'total_saving_80ggc',total_saving_80ggc
#                 print 'limit_80ggc',limit_80ggc
#                 print "total_saving_80tta = ",total_saving_80tta
#                 print 'limit_8080tta = ',limit_80tta
#                  
#                  
#                 print ""
#                 print ""
#                 print ""
#  
#  
 
  
#========================== Total  Calculations =======================
                 
                total_gross=gross_basic+gross_hra+gross_da+gross_tca+gross_spa+gross_sch+gross_med+other_income
                 
#                 print'Total gross  ',total_gross
                 
                total_exmp=exmp_basic+exmp_hra+exmp_da+exmp_tca+exmp_spa+exmp_sch+exmp_med
#                 total_net=net_basic+net_hra+net_da+net_tca+net_pf+net_spa+net_sch+net_med
                total_net=total_gross-total_exmp
                 
#=========================== Deductions  ============================
                total_saving_80c=total_saving_80c+gross_pf
                 
                 
#                 print 'total_saving_80c',total_saving_80c
#                 print 'limit_80c',limit_80c
#                 print ""
#                 print ""
#                 print ""
                 
                if limit_80c<total_saving_80c:
                    total_saving_80c=limit_80c
                 
#                 print 'total_saving_80c',total_saving_80c
#                 print 'limit_80c',limit_80c
                 
                if net_hra>hra_saving:
                    hra_deductions=round (hra_saving-(net_basic*.10))
                    if hra_deductions<0:
                        hra_deductions=0
                elif net_hra<hra_saving:
                    hra_deductions=round (net_hra-(net_basic*.10))
                 
                 
                 
                 
                 
                net_exemption=total_exmp+total_saving_80c+hra_deductions+total_saving_80cccd_1b+total_saving_24+total_saving_80e+total_saving_80ccg+total_saving_80d_parents+total_saving_80d_self+total_saving_80ddb+total_saving_80u+total_saving_80dd+total_saving_80g+total_saving_80ggc+total_saving_80tta
                total_net_after_80c=total_net-exmp_80c
                 
#=========================== Total Taxable ====================                
                 
                total_tax_income=total_gross-net_exemption
  
                for tax_income in self.env['tax.slabs'].search([]):
#                     print 'TAX   INCOME ==============',tax_income.name,tax_income.from_limit,tax_income.to_limit,tax_income.percent
                    if tax_income.name=='Slab I':
                        slab1_fromlimit=tax_income.from_limit
                        slab1_tolimit=tax_income.to_limit
                        slab1_percent=tax_income.percent
                    
                    if tax_income.name=='Slab II':
                        slab2_fromlimit=tax_income.from_limit
                        slab2_tolimit=tax_income.to_limit
                        slab2_percent=tax_income.percent
                        
                    if tax_income.name=='Slab III':
                        slab3_fromlimit=tax_income.from_limit
                        slab3_tolimit=tax_income.to_limit
                        slab3_percent=tax_income.percent
                        
                    if tax_income.name=='Slab IV':
                        slab4_fromlimit=tax_income.from_limit
                        slab4_tolimit=tax_income.to_limit
                        slab4_percent=tax_income.percent
                        
                        
                        
                        
#                 print 'SLAB 1',slab1_fromlimit,slab1_tolimit,slab1_percent
#                 print 'SLAB 2',slab2_fromlimit,slab2_tolimit,slab2_percent
#                 print 'SLAB 3',slab3_fromlimit,slab3_tolimit,slab3_percent
#                 print 'SLAB 4',slab4_fromlimit,slab4_tolimit,slab4_percent
               
                
                        
 
                if (total_tax_income)>slab1_fromlimit and (total_tax_income)<slab1_tolimit:
                     
                    deduction_12_mnth=0
                    deduction_curr_mnth=0
                    deduction_12_mnth_cess=0
                    deduction_curr_mnth_ps=-deduction_curr_mnth
                    self.env.cr.execute("update hr_payslip_line set total=%s,amount=%s where slip_id=%s and code='TDS';",(deduction_curr_mnth_ps,deduction_curr_mnth_ps,sl))
                    self.env.cr.execute("update hr_payslip_line set total=(select total from hr_payslip_line where code='NET' and slip_id=%s)-%s,amount=(select total from hr_payslip_line where code='NET' and slip_id=%s)-%s where slip_id=%s and code='NET';",(sl,deduction_curr_mnth,sl,deduction_curr_mnth,sl))
                
                elif (total_tax_income)>slab2_fromlimit and (total_tax_income)<slab2_tolimit:
                     
                    deduction_12_mnth=((total_tax_income)-250000)*(slab2_percent/100)
                    deduction_12_mnth_cess=round(deduction_12_mnth+deduction_12_mnth*.03)
# =====================changes tax=====================
                    deduction_12_mnth_cess=deduction_12_mnth_cess-actual_tds
                    deduction_curr_mnth=round(deduction_12_mnth_cess/((term-month)+1))
                    
# =====================changes tax=====================
#                     deduction_curr_mnth=round(deduction_12_mnth_cess/12)
                    deduction_curr_mnth_ps=-deduction_curr_mnth
                    
                    self.env.cr.execute("update hr_payslip_line set total=%s,amount=%s where slip_id=%s and code='TDS';",(deduction_curr_mnth_ps,deduction_curr_mnth_ps,sl))
                    self.env.cr.execute("update hr_payslip_line set total=(select total from hr_payslip_line where code='NET' and slip_id=%s)-%s,amount=(select total from hr_payslip_line where code='NET' and slip_id=%s)-%s where slip_id=%s and code='NET';",(sl,deduction_curr_mnth,sl,deduction_curr_mnth,sl))
                                 
                elif (total_tax_income)>slab3_fromlimit and (total_tax_income)<slab3_tolimit:
                    tot=total_tax_income
                     
                    deduction_12_mnth=12500 +((tot)-500000)*(slab3_percent/100)
                    deduction_12_mnth_cess=round(deduction_12_mnth+deduction_12_mnth*.03)
# =====================changes tax=====================
                    deduction_12_mnth_cess=deduction_12_mnth_cess-actual_tds
                    deduction_curr_mnth=round(deduction_12_mnth_cess/((term-month)+1))
                    
# =====================changes tax=====================
 
#                     deduction_curr_mnth=round(deduction_12_mnth_cess/12)
                    deduction_curr_mnth_ps=-deduction_curr_mnth

                    self.env.cr.execute("update hr_payslip_line set total=%s,amount=%s where slip_id=%s and code='TDS';",(deduction_curr_mnth_ps,deduction_curr_mnth_ps,sl))
                    self.env.cr.execute("update hr_payslip_line set total=(select total from hr_payslip_line where code='NET' and slip_id=%s)-%s,amount=(select total from hr_payslip_line where code='NET' and slip_id=%s)-%s where slip_id=%s and code='NET';",(sl,deduction_curr_mnth,sl,deduction_curr_mnth,sl))
               
                elif (total_tax_income)>slab4_fromlimit and (total_tax_income)<slab4_tolimit:
                    deduction_12_mnth=112500+((total_tax_income)-1000000)*(slab4_percent/100)
                    deduction_12_mnth_cess=round(deduction_12_mnth+deduction_12_mnth*.03)
 
# =====================changes tax=====================
                    deduction_12_mnth_cess=deduction_12_mnth_cess-actual_tds
                    deduction_curr_mnth=round(deduction_12_mnth_cess/((term-month)+1))
                    
# =====================changes tax=====================
 
 
#                     deduction_curr_mnth=round(deduction_12_mnth_cess/12)
                    deduction_curr_mnth_ps=-deduction_curr_mnth
                                        
                    self.env.cr.execute("update hr_payslip_line set total=%s,amount=%s where slip_id=%s and code='TDS';",(deduction_curr_mnth_ps,deduction_curr_mnth_ps,sl))
                    self.env.cr.execute("update hr_payslip_line set total=(select total from hr_payslip_line where code='NET' and slip_id=%s)-%s,amount=(select total from hr_payslip_line where code='NET' and slip_id=%s)-%s where slip_id=%s and code='NET';",(sl,deduction_curr_mnth,sl,deduction_curr_mnth,sl))
#                 print 'projected_taxable',actual_taxable
#                 print 'actual_taxable',projected_taxable
#                 
#                 
#                 if gross_pf>ded_lim:
#                     deduc_80c=ded_lim
#                 else:
#                     deduc_80c=gross_pf
#                     
#                 total_amount=gross_basic+gross_hra+gross_da+gross_tca+gross_sch+gross_spa
#                 total_exmpt_amt=exempt_tca+exempt_basic+exempt_hra+exempt_da
#                 total_exmpt_amt_sav=exempt_tca+exempt_basic+exempt_hra+exempt_da+deduc_80c
#                 tot_tax_after_80c=total_amount-total_exmpt_amt
#                 total_taxable_amt=total_amount-total_exmpt_amt_sav
#                 net_taxable=gross_basic+gross_hra+gross_da+taxable_tca-net_taxable
#                 
#                 
#====================================TDS Form CREATED =================================================               
#                
                a = self.env['employee.tds'].search([('employee_id','=',emp),('date_from','=',date_frm),('date_to','=',date_to)])
                print'kkkkkkkkkkksssssssssssssssskkkkkk' ,a
      
                        
                if a:
            
                    self.env.cr.execute("update employee_tds set employee_id=%s,fin_year_id=%s,tds_gross_amount=%s,tds_net_salary_taxable=%s,net_tds_amount=%s,net_tds_paid=%s where date_from=%s and date_to=%s and employee_id=%s ;",(emp,fin_year,total_gross,total_tax_income,deduction_12_mnth_cess,actual_tds,date_frm,date_to,emp))
                else:
                    self.env.cr.execute("insert into employee_tds (employee_id,fin_year_id,date_from,date_to,name,tds_gross_amount,tds_net_salary_taxable,net_tds_amount,net_tds_paid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s);",(emp,fin_year,date_frm,date_to,tax_sheet,total_gross,total_tax_income,deduction_12_mnth_cess,actual_tds))
                  
                b = self.env['employee.tds'].search([('employee_id','=',emp),('date_from','=',date_frm),('date_to','=',date_to)])
      
                slip.tds_id=b.id
                  
                emp_tds_id = b.id 
                  
                print 'employee_tds_id=========',emp_tds_id
#                  
#                 print '=================+SLIP==========================+==',sl    
                     
                 
                 
                      
                 
                 
                 
            print'kkkkkkkkkkksssssssssssssssskkkkkk' ,date_frm      
             
            self.env.cr.execute("delete from employee_tds_line where employee_tds_id=%s;",(emp_tds_id,))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Basic Pay',%s,%s,%s,%s);",(gross_basic,exmp_basic,net_basic,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Dearness Allowance',%s,%s,%s,%s);",(gross_da,exmp_da,net_da,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Vehicle And Conveyance Allowance',%s,%s,%s,%s);",(gross_tca,exmp_tca,net_tca,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Special Allowance',%s,%s,%s,%s);",(gross_sch,exmp_sch,net_sch,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Other Allowance',%s,%s,%s,%s);",(gross_spa,exmp_spa,net_spa,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Medical Allowance',%s,%s,%s,%s);",(gross_med,exmp_med,net_med,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('House Rental Allowance',%s,%s,%s,%s);",(gross_hra,exmp_hra,net_hra,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
             
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('INCOME FROM OTHER SOURCES(House Property, SAVING/AC Intrest etc)',%s,0,%s,%s);",(other_income,other_income,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
 
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('TOTAL',%s,%s,%s,%s);",(total_gross,total_exmp,total_net,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
 
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Provident Fund',%s,0,%s,%s);",(gross_pf,gross_pf,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
            self.env.cr.execute("insert into employee_tds_line (name,employee_tds_id) values('DEDUCTIONS',%s);",(emp_tds_id,))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('HRA Deductions',0,%s,0,%s);",(hra_deductions,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
 
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80C)',0,%s,0,%s);",(total_saving_80c,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80CCD(1B))',0,%s,0,%s);",(total_saving_80cccd_1b,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(24)',0,%s,0,%s);",(total_saving_24,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80E)',0,%s,0,%s);",(total_saving_80e,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80CCG)',0,%s,0,%s);",(total_saving_80ccg,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80D(parents))',0,%s,0,%s);",(total_saving_80d_parents,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80D(self))',0,%s,0,%s);",(total_saving_80d_self,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80DDB)',0,%s,0,%s);",(total_saving_80ddb,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80U)',0,%s,0,%s);",(total_saving_80u,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80DD)',0,%s,0,%s);",(total_saving_80dd,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80G)',0,%s,0,%s);",(total_saving_80g,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80GGC)',0,%s,0,%s);",(total_saving_80ggc,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('Deductions under sec(80TTA)',0,%s,0,%s);",(total_saving_80tta,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
            self.env.cr.execute("insert into employee_tds_line (name,total_amount,exempted_amount,taxable_amount,employee_tds_id) values('TOTAL Taxable Income',%s,%s,%s,%s);",(total_gross,net_exemption,total_tax_income,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
            self.env.cr.execute("insert into employee_tds_line (employee_tds_id) values(%s);",(emp_tds_id,))
 
            self.env.cr.execute("insert into employee_tds_line (name,taxable_amount,employee_tds_id) values('Deductions for 12 months',%s,%s);",(deduction_12_mnth,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,taxable_amount,employee_tds_id) values('Deductions for 12 months with 3 percent cess',%s,%s);",(deduction_12_mnth_cess,emp_tds_id))
            self.env.cr.execute("insert into employee_tds_line (name,taxable_amount,employee_tds_id) values('Deductions for current month',%s,%s);",(deduction_curr_mnth,emp_tds_id))
 
#================================= INCOME TAX COMPUTED ==============================================
         
            
            
            
            
            
            
#         access=0
#         global employee
#         for slip in self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)]):
#             
#             
        return True


#     @api.multi
#     def compute_sheet(self):
#         for payslip in self:
#             number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
#             #delete old payslip lines
#             print 'NNNNNUMBERRRR',number
#             
#             payslip.line_ids.unlink()
#             # set the list of contract for which the rules have to be applied
#             # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
#             contract_ids = payslip.contract_id.ids or \
#                 self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
#             lines = [(0, 0, line) for line in self.get_payslip_lines(contract_ids, payslip.id)]
#             payslip.write({'line_ids': lines, 'number': number})
#         return True
#     
global flag
global max_id    
flag=0
max_id=0


 
class hr_payslip_employees_inherit(models.TransientModel):
 
    _inherit ='hr.payslip.employees'
    flag=0
    max_id=0
    
    @api.multi
    def compute_sheet(self):
          
        print '====================checllllll;;;;;;;;kkkkkkkk '
#         print 'kajkjkjjjkjkjkjk',flag
        if flag==0:
            self.env.cr.execute("select coalesce(max(id),0) from hr_payslip_line;")
            global max_id
            max_id = self.env.cr.fetchone()[0]  
#             print '----a-a-a-a-a-a-a-a-a-',max_id
        global flag
        flag=1
              
              
        payslips = self.env['hr.payslip']
#         print "payslipsssssssssssssssssss",payslips,'klasdjalksjaslkfjalksjdlkjm'

        
        [data] = self.read()
        active_id = self.env.context.get('active_id')
 
        if active_id:
#             [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note','journal_id','fin_year'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        jour_id= run_data.get('journal_id')[0]
        f_yr=run_data.get('fin_year')[0]
        
        if not data['employee_ids']:
            raise ValidationError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'journal_id':jour_id,
                'fin_year':f_yr,
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
            }
            

            payslips += self.env['hr.payslip'].create(res)
        
        
        print'PAYSLIPSSSSS',payslips
        
        payslips.compute_sheet()

# ===================== payslip redundancy check ================================          

#         for slip_id in payslips:
# #             print 'slip_id',slip_id.date_to,slip_id.date_from
#             
#             for payslip_id in self.env['hr.payslip'].search([]):
#                 if payslip_id.employee_id==slip_id.employee_id:
#                     if payslip_id.date_to==slip_id.date_to and payslip_id.date_from==slip_id.date_from and payslip_id.state==slip_id.state:
#                         print'same payslip found'
#                     else:
#                         slip_id.compute_sheet()
# ===================== payslip redundancy check ================================  
        
        test=self.env['hr.payslip.run'].search([])
        for t in test:
            value=t.fin_year
            a = self.env['hr.payslip'].search([])
            for i in a:
                i.fin_year =value.id
        return {'type': 'ir.actions.act_window_close'}    
    
    
    
global runflag
runflag=0  

class hr_payslip_run_inherit(models.Model):
    _inherit = 'hr.payslip.run'
    
    fin_year=fields.Many2one('account.fiscalyear', 'Financial Year')
    
    
    @api.multi
    def close_payslips(self):
        stat =self.env['hr.payslip'].search([('payslip_run_id','=', self.id)])
        if stat:
            for i in stat:
#                 print "=============++++++!!!!!!!%^&*()_",i.state,i.number
                i.state='done'
        else:
            raise ValidationError(_('No Payslips Present to Close'))   
    
    
    @api.multi
    def close_payslip_run(self):
        maxid=max_id
        print 'MAXIIIIIIDDDDDD BEFORE',maxid
        stat =self.env['hr.payslip.run'].search([('name', '=', self.name)],limit=1)
        for status in stat:
            slip_id = status.slip_ids
            if not slip_id:
                raise ValidationError(_('You Cannot Close a Batch without Selecting any employee'))
            else:
                for r in slip_id:
                    for s in self.env['hr.payslip'].search([]):
                        if s.id==r.id:
                            if s.state=='draft':
                                raise ValidationError(_('You Cannot Close a Batch with Payslip(s) In Draft State'))
                            else:
#                                 print 'PRINT MAX ID',maxid
                                global runflag
                                runflag=1
                                
        if runflag==1:
            self.env.cr.execute("select coalesce(max(id),0) from pay_image;")
            print 'max_id---------',self.env.cr.fetchone()[0] 
            self.env.cr.execute("""insert into pay_image(employee_id,pay_code,amount,fin_year,yymm)select hl.employee_id,hl.code,hl.total,(select distinct fin_year from hr_payslip hr where hr.id=hl.slip_id),
                                (select replace((to_char((select distinct date_to from hr_payslip hr where hr.id=hl.slip_id), 'YYYY-MM')),'-','')::integer) as yymm
                                 from hr_payslip_line hl left join hr_payslip hr on hr.id=hl.slip_id where hr.state!='draft' and hl.id> %s order by employee_id""",(maxid,))
           
            self.env.cr.execute("select coalesce(max(id),0) from pay_image;")
            print 'max_id---------',self.env.cr.fetchone()[0] 

            global runflag
            runflag=0
        
        self.env.cr.execute("select coalesce(max(id),0) from hr_payslip_line;")
        global max_id
        max_id = self.env.cr.fetchone()[0]  
        print 'PRINT MAX ID AFTER',max_id
        
        
        return self.write({'state': 'close'})
    
    


    
class employee_tds(models.Model):
    _name = 'employee.tds'
    
    
#     @api.multi
#     def get_employee(self):
#         self.name= 'Income tax for '+self.employee_id.name_related
    
    
    
    name = fields.Char(string='Name')
    employee_id = fields.Many2one('hr.employee','Employee')
    tds_run_id = fields.Many2one('employee.tds.run','Run Id',copy=False)
    region_id = fields.Char('Region')
    tds_basic_amount = fields.Float('Basic Amount')
    tds_allowance_amount = fields.Float('Allowance Amount')
    tds_gross_amount = fields.Float('Gross Amount')
    tds_deduction_amount = fields.Float('Deduction Amount')
    tds_rebate_amount = fields.Float('Rebate Amount')
    tds_net_salary_taxable = fields.Float('Net Taxable Amount')
    net_tds_amount = fields.Float('Net Income Tax Amount')
    net_tds_paid = fields.Float('Income Tax Amount Paid')
    professional_tax_paid = fields.Float('Professional Tax Paid')
    cpf_paid = fields.Float('CPF Paid')
    gis_paid = fields.Float('GIS Paid')
    eps_paid = fields.Float('EPS Paid')
    lic_paid = fields.Float('LIC Paid')
    vpf_paid = fields.Float('VPF Paid')
#     company_id = fields.Many2one('res.company','Zone')
    tds_line_ids = fields.One2many('employee.tds.line','employee_tds_id','Income Tax Lines')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    fin_year_id = fields.Many2one('account.fiscalyear','Financial Year')
#     unit_id = fields.Many2one('employee.unit','Unit')
    professional_tax_monthly = fields.Float('Professional Tax Monthly')
    cpf_monthly = fields.Float('CPF Monthly')
    gis_monthly = fields.Float('GIS Monthly')
    lic_monthly = fields.Float('LIC Monthly')
    vpf_monthly = fields.Float('VPF Monthly')
    medical_expense_monthly = fields.Float('Medical Expense Monthly')
    medical_expense_paid = fields.Float('Medical Expense Paid')
    total_taxable_amount = fields.Float('Total Taxable Amount')
    
    state =  fields.Selection([
    ('draft', 'Draft'),
    ('done', 'Done')
     ], 'Status', select=True, readonly=True, copy=False)
    
    def get_tax_lines(self, obj):
            tax_line = self.env['employee.tds.line'].search([('employee_tds_id','=',self.id)])
            res = []
            ids = []
            
            
            for id in range(len(obj)):
                if obj[id]:
                    ids.append(obj[id].id)
            if ids:
                res = tax_line.search([('employee_tds_id','=',self.id)])
            return res
    
    
class employee_tds_line(models.Model):
    _name = 'employee.tds.line'
    
    
    
    name = fields.Char('Name')
    employee_tds_id = fields.Many2one('employee.tds','Employee Income Tax',ondelete='cascade')
    total_amount = fields.Float('Total Amount')
    exempted_amount = fields.Float('Exempted Amount')
    taxable_amount = fields.Float('Taxable Amount')
    
             
# class employee_tds_run(models.Model):
#     _name = 'employee.tds.run'
#     
# #     def create(self, cr, uid, vals, context=None):
# #         if 'date_from' in vals and vals['date_from']:
# #             date_from = vals['date_from']
# #             print"date_from====",date_from
# #         if 'company_id' in vals and vals['company_id']:
# #             company_id = vals['company_id']
# #             print"company_id====",company_id
# #             employee = self.pool.get('employee.tds.run').search(cr, uid, [('company_id', '=', company_id),('date_from', '=', date_from)], context=context)
# #             
# #             print '===================',employee
# #             
# #             if employee:
# #                 raise ValidationError(_('Employee Income Tax Batch record already exists! Please update Or Delete the existing record.'))
# #         return super(employee_tds_run, self).create(cr, uid, vals, context=context)
# #     
# #     def compute_tax(self, cr, uid, ids, context=None):
# #         for tds in self.browse(cr,uid,ids,context=context):
# #             a = int(tds.company_id)
# #             date_from = "'"+ tds.date_from +"'"
# #             print"date_from",date_from
# #             date_to = "'"+ tds.date_to +"'"
# #             print"date_to",date_to
# #              cr.execute("SELECT(c_tds(%s,%s,%s,%s,%s))",(date_from,date_to,a,'',2));
# #             print"successful"
# #             res = cr.fetchall()
# #             self.write(cr, uid, ids , {'message': 'Income Tax computed successfully!'}, context=context)
# #         return res
#     
#     
#     @api.multi
#     def compute_tax(self):
#         
#         tax_obj=self.env['hr.payslip']
#         
#         [data] = self.read()
#         print '+++++++++++',data
#         active_id = self.env.context.get('active_id')
#         
#         print '+++++++++++()()()()()()()()',active_id
# 
#         for slip in self.env['hr.payslip'].search([('date_from', '=', self.date_from),('date_to', '=', self.date_to),('state','=','done')]):
#             print'====================',slip
#     
#     
#     
#   
#     name = fields.Char('Name',required='True')
#     tds_ids = fields.One2many('employee.tds','tds_run_id','Income Tax')
#     state = fields.Selection([
#     ('draft', 'Draft'),
#     ('done', 'Done'),
#      ], 'Status', select=True, readonly=True, copy=False, default='draft')
#     date_from = fields.Date('Date From',required='True')
#     date_to = fields.Date('Date To',required='True')
#     company_id = fields.Many2one('res.company','Zone')
#     message = fields.Char('Message',readonly='True')
#                
#     _defaults = {
#         'date_from': lambda *a: time.strftime('%Y-%m-01'),
#         'date_to': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
#                  }
#     def confirm_sheet(self, cr, uid, ids, context=None):
#         for tds in self.browse(cr,uid,ids,context=context):
#             if not tds.message:
#                 raise ValidationError(_('Please Compute Income Tax First'))
#         return self.write(cr, uid, ids, {'state': 'done'}, context=context)
#     def unlink(self, cr, uid, ids, context=None):
#         for tds_run in self.browse(cr, uid, ids, context=context):
#             if tds_run.state not in  ['draft']:
#                 raise ValidationError(_('You cannot delete a income tax batch which is not draft!'))
#         return super(employee_tds_run, self).unlink(cr, uid, ids, context)  
    
    
    

    
                       
# class wrapped_income_tax_details(models.AbstractModel):
#     _name = 'report.hr_tds.tax'
#     _inherit = 'report.abstract_report'
#     _template = 'hr_tds.tax'
#     _wrapped_report_class = income_tax_details_report


 

        
    
