# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, api, fields, _


class ProjectTaskIn(models.Model):
    _inherit = 'project.task'


    report_date = fields.Date(string="Report Date")
    schedule_date = fields.Datetime(string="Schedule Date")
    reference = fields.Char(string="Reference")
    attn = fields.Selection([('mr','Mr.'),('mrs','Mrs.'),('miss', 'Miss.'),('dr','Dr.'),('prof','Prof.')], string="Attn Title")
    first_name = fields.Char(string='First Name')
    family_name = fields.Char(string="Family Name")
    job_title = fields.Char(string="Job Title")
    start_time = fields.Char(string="Start Time", size=4)
    end_time = fields.Char(string="End Time", size=4)
    contact_person = fields.Char(string="Contact Person")
    partner_id = fields.Many2one('res.partner',
        string='M/s',
        default=lambda self: self._get_default_partner(),
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    ingredients = fields.One2many('project.task.line', 'ingredient')
    quantity = fields.Float(string="Quantity")
    where_applied = fields.Char(string="Where applied")
    image_ids = fields.One2many('images.images', 'image_id', string="New Images")
    technical_crew = fields.Many2many('technical.crew', string="Technical Crew")
    covered_area = fields.Char(string="Covered Areas")
    recommendations = fields.Many2many('recommendation.recommendation', string="Recommendations")
    activities = fields.Selection([('pest_activity', 'Pest activity'),('no_pest_activity','No Pest activity')], string="Activity")
    find_and_remark = fields.Many2many('find.remark', string="Pest Activity")
    number_id = fields.Char(string="Report Number")

    choose_coordinator = fields.Many2one('res.partner',string="Choose Coordinator")
    phone = fields.Char(string="Phone")
    job_position = fields.Char(string="Job Position")

    # PEST MANAGEMENT DEVICES - PMD
    pwds = fields.One2many('pmd.pmd', 'pmd', string="Pest management Devices")
    location = fields.Text(string="Location")
    show_on_report_following_area_visit = fields.Boolean(string="Show on Report")
    show_on_report_up_callback = fields.Boolean(string="Show on Report")
    show_on_report_itls = fields.Boolean(string="Show on Report")
    operational_during_the_visit = fields.Text(string="Following areas were not inspected/treated as it was found closed/locked - operational during the visit")
    up_callback = fields.Selection([('callback_1','Due to the fact that your esteemed staff reported to have seen XXX at XXX, our technical crew attended and upon thorough inspection no pest activity was found during the visit; however, the above mentioned preventative treatment was done additionally.'),
                                ('callback_2', 'Due to the fact that your esteemed staff reported to have seen XXX at XXX, our technical crew attended and upon thorough inspection XXX were found at XXX and the above mentioned treatment was done.'),
                                ('callback_3', 'This extra Follow Up visit was done to monitor the pest activity at your esteemed premises, and upon inspection, the above mentioned treatments were done.')], string="Select Follow Up/Callback")
    select_ilts = fields.Selection([('ilts_1', 'Additionally, all installed “Insect light traps supplied by KPHC” were checked by our technical crew and no action was required during the visit.'),
                                ('ilts_2', 'Additionally, our technical crew offered to replace the Insects light traps glue board, unfortunately, the store was out of stock of glue board during the visit.'),
                                ('ilts_3', 'Additionally, all installed “Insect light traps supplied by KPHC” were checked by our technical crew and glue boards were replaced.')],
                                 string="Select ILTs")  
    type_of_service = fields.Selection([('base_treatment', 'Base Treatment'),('replenishing_treatment','Replenishing Treatment'),
                                           ('regular_inspection','Regular Inspection'),('control_treatment_c1','Control Treatment (C1)'),
                                           ('control_treatment_c2','Control Treatment (C2)'),('control_treatment_c3','Control Treatment (C3)'),
                                           ('control_treatment_c4','Control Treatment (C4)'),('follow_up','Follow Up'),('inspection','Inspection'),
                                           ('callback','Callback'),('ficp','FICP')], string="Type of Service")

    def _default_worksheet_template_id(self):
        default_project_id = self.env.context.get('default_project_id')
        if default_project_id:
            project = self.env['project.project'].browse(default_project_id)
            return project.worksheet_template_id
        return False
        
    worksheet_template_id = fields.Many2one('project.worksheet.template', string="Worksheet Template", default=_default_worksheet_template_id)

    @api.onchange('choose_coordinator')
    def _onchange_user(self):
        for rec in self:
           rec.phone = rec.choose_coordinator.phone
           rec.job_position = rec.choose_coordinator.function

    def images_group(self):
        dataDict = {}
        for rec in self.image_ids:
            dataDict.setdefault(rec.name,[])
            dataDict[rec.name].append({'image': rec.image})
        return dataDict 

class ProjectTaskLine(models.Model):
    _name = 'project.task.line'
    _description = "project task line"
    _rec_name = 'ingredient'

    ingredient = fields.Many2one('project.task', string="Ingredient")
    ingredients = fields.Many2one('ingredient.product', string="Ingredients")
    quantity = fields.Float(string="Quantity")
    product_uom_id = fields.Many2one('ingredient.uom', string='Unit of Measure') 
    where_applied = fields.Char(string="Where applied")
    applied_against = fields.Selection([('crawling_insects', 'Crawling Insects'), ('flying_insects', 'Flying Insects'),
                                        ('crawling_and_flying_insects', 'Crawling and Flying Insects'),
                                        ('rodents', 'Rodents'),('monitoring_pest_activity', 'Monitoring Pest Activity'),
                                        ('parasites', 'Parasites'),('crawling_insects_and_parasites', 'Crawling Insects and Parasites'),
                                        ('cats', 'Cats'),
                                        ])


class Images(models.Model):
    _name = 'images.images'
    _description= 'image view'
    _rec_name = 'image_id'

    image = fields.Binary(string="Image")
    name = fields.Char(string="Title")
    image_id = fields.Many2one('project.task', string="New Images")



class TechnicalCrew(models.Model):
    _name = 'technical.crew'
    _description = 'technical crew'
    _rec_name = 'name'

    name = fields.Char(string="technical Crew")


class Recommendations(models.Model):
    _name ='recommendation.recommendation'
    _description = 'recommendation table'
    _rec_name = 'name'

    name = fields.Char(string="Recommendations")


class FindRemark(models.Model):
    _name = 'find.remark'
    _description = 'find and remark'
    _rec_name = 'name'

    name = fields.Char(string="Find and Remark")


class Pwd(models.Model):
    _name = 'pmd.pmd'
    _description = 'Pest management Devices'
    _rec_name = 'pmd'

    pmd = fields.Many2one('project.task', string="Pest management Devices")
    type_id = fields.Selection([('rbs','RBS'),('rts','RTS'),('glue_trap','Glue Trap'), ('bait_tray', 'Bait Tray')], string="Type")
    qty = fields.Char(string="Quantity")
    location = fields.Char(string="Location")
    pest_activity = fields.Selection([('consumption', 'Consumption'),('no_consumption', 'No Consumption'),
                                      ('catch', 'Catch'),('no_catch', 'No Catch')       
                                    ], string="Pest Activity")
    status = fields.Selection([('functional', 'Functional'),('damaged','Damaged'),
                               ('Missing', 'Missing'),('spoiled','Spoiled'),('dusty', 'Dusty'),
                               ('newly_placed','Newly Placed')
                            ],string="Status")
    action = fields.Selection([('na', 'NA'),('replenished','Replenished'),('replaced','Replaced')])
    serial_no = fields.Char(string="Serial No")
