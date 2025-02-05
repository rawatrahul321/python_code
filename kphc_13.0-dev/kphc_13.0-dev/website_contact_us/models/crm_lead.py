from odoo import api, fields, models, SUPERUSER_ID

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    school_university = fields.Char(string="Organization Name")
