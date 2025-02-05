# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from dateutil.parser import parse
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportPosBalamce(models.AbstractModel):

    _name = 'report.caret_united18_pos.report_pos_balance'

    @api.model
    def get_pos_details(self, start_date=False, company_id=False):

        PosOrder = self.env['pos.order']
        if not company_id:
            self.env.cr.execute("""
                    SELECT
                        id
                        FROM
                            pos_order
                        WHERE
                            date(date_order) = %s
            """, ([start_date]))
        else:
            self.env.cr.execute("""
                    SELECT
                        id
                        FROM
                            pos_order
                        WHERE
                            date(date_order) = %s
                            AND company_id = %s
            """, ([start_date, company_id]))
        pos_orders = [res['id'] for res in self.env.cr.dictfetchall()]
        data = {}
        for order in PosOrder.sudo().browse(pos_orders):
            data.setdefault(order.company_id.id, {
                    'company_name': order.company_id.name,
                    'amount': [],
                    'amount_total': 0,
                })
            recordRow = data[order.company_id.id]
            recordRow['amount'].append(order.amount_total)
            recordRow['amount_total'] = sum(recordRow['amount'])
        return data

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update({'result': self.get_pos_details(data.get('start_date'), data.get('company_id'))})
        data.update({'start_date':datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()})
        return data
