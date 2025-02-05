# -*- coding: utf-8 -*-

from odoo import tools,models, fields, api, _
import xlwt
from datetime import datetime

class PosBalanceWizard(models.TransientModel):
    _name = 'pos.balance.wizard'
    _description = 'pos balance Report'

    start_date = fields.Date(required=True, string='Date', default=fields.datetime.today())
    company_id = fields.Many2one('res.company', string='Company')

    @api.multi
    def generate_pos_balance_report(self):
        return self.env.ref('caret_united18_pos.pos_balance_report').report_action([],
                                                                        data={'start_date': self.start_date,
                                                                                'company_id': self.company_id.id or False,
                                                                              })
