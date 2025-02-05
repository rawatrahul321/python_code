# -*- coding: utf-8 -*-

from odoo import tools,models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class StockMoveWizard(models.TransientModel):
    _name = 'stock.move.wizard'
    _description = 'Open Inventory Report'

    @api.model
    def _default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id

    start_date = fields.Datetime(required=True, string='Start date')
    end_date = fields.Datetime(required=True, string='End date', default=fields.datetime.now())
    location_id = fields.Many2one('stock.location', string='Stock Location',
                                 domain=[('usage','=','internal'),('return_location','=',False)],
                                 default=_default_location_id,
                                 required=True)

    @api.multi
    def generate_stock_report(self):
        return self.env.ref('caret_united18_custom.stock_move_report').report_action([],
                                                                        data={'start_date': self.start_date,
                                                                              'end_date': self.end_date,
                                                                              'location_id': self.location_id.id})
