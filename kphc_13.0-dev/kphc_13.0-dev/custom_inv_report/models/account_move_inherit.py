# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    cen_code = fields.Char(string="CEN Code", help="Salesperson code")

    @api.onchange('x_studio_pop_end_date')
    def _onchange_end_date(self):
        if self.x_studio_pop_end_date and self.invoice_date and self.x_studio_pop_end_date < self.invoice_date:
            self.x_studio_pop_end_date = self.invoice_date

    @api.onchange('x_studio_pop_start_date_1')
    def _onchange_start_date(self):
        if self.x_studio_pop_start_date_1 and self.invoice_date and self.x_studio_pop_start_date_1 < self.invoice_date:
            self.x_studio_pop_start_date_1 = self.invoice_date
