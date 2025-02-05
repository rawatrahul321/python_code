# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from dateutil import parser
from datetime import datetime
from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class ReportStockDetails(models.AbstractModel):

    _name = 'report.caret_united18_custom.report_stocketails'

    @api.model
    def get_begining_qty(self, start_date, product_id,location_id):
        incoming_qry = """ SELECT sum(product_uom_qty) as incoming_qty 
                        FROM
                            stock_move
                        WHERE date < %s
                            AND state = 'done'
                            AND product_id = %s
                            AND location_dest_id = %s
                    """
        outgoing_qry = """ SELECT sum(product_uom_qty) as outgoing_qty 
                        FROM
                            stock_move
                        WHERE date < %s
                            AND state = 'done'
                            AND product_id = %s
                            AND location_id = %s
                    """
        param = (start_date, product_id.id, location_id)
        self.env.cr.execute(incoming_qry, param)
        incoming = self.env.cr.dictfetchall()[0]['incoming_qty'] or 0
        self.env.cr.execute(outgoing_qry, param)
        outgoing = self.env.cr.dictfetchall()[0]['outgoing_qty'] or 0
        total = incoming-outgoing
        return total

    @api.model
    def get_sale_details(self, start_date=False, end_date=False,location_id=False):

        self.env.cr.execute("""
                    SELECT
                        id
                        FROM
                            stock_move
                        WHERE
                            date >= %s
                        AND date <= %s
                        AND state = 'done'
                        AND location_id = %s
                UNION
                    SELECT
                        id
                        FROM
                            stock_move
                        WHERE
                            date >= %s
                        AND date <= %s
                        AND state = 'done'
                        AND location_dest_id = %s
        """, (start_date, end_date, location_id, start_date, end_date, location_id))
        StockMove = [res['id'] for res in self.env.cr.dictfetchall()]
        data = {}
        for move in self.env['stock.move'].browse(StockMove):
            incoming = 0
            outgoing = 0
            internal = 0
            if move.location_id.id == location_id and move.location_dest_id.id != location_id:
                outgoing = move.product_uom_qty
            if move.location_id.id != location_id and move.location_dest_id.id == location_id:
                incoming = move.product_uom_qty
            if move.location_id.id == location_id and move.location_dest_id.id == location_id:
                internal = move.product_uom_qty
            data.setdefault(move.product_id.name, {
                    'beginning': 0,
                    'record': move.product_id,
                    'incoming': [],
                    'total_incoming': 0,
                    'outgoing': [],
                    'total_outgoing': 0,
                    'internal': [],
                    'total_internal': 0,
                })
            recordRow = data[move.product_id.name]
            recordRow['outgoing'].append(outgoing)
            recordRow['incoming'].append(incoming)
            recordRow['internal'].append(internal)
            recordRow['total_outgoing'] = int(sum(recordRow['outgoing']))
            recordRow['total_incoming'] = int(sum(recordRow['incoming']))
            recordRow['total_internal'] = int(sum(recordRow['internal']))
        for row in data:
            beginning = self.get_begining_qty(start_date, data[row]['record'], location_id)
            data[row]['beginning'] = int(beginning)

        return data

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        total_begining = 0
        total_incoming = 0
        total_outgoing = 0
        total_internal = 0
        total_end = 0
        result = {'start_date':parser.parse(data.get('start_date')).date(),
                  'end_date':parser.parse(data.get('end_date')).date(),
                  'result': self.get_sale_details(data.get('start_date'),
                                                    data.get('end_date'),
                                                    data.get('location_id'))}
        for res in result['result']:
            total_begining = total_begining + result['result'][res]['beginning']
            total_incoming = total_incoming + result['result'][res]['total_incoming']
            total_outgoing = total_outgoing + result['result'][res]['total_outgoing']
            total_internal = total_internal + result['result'][res]['total_internal']
            total_end = total_end +  result['result'][res]['record'].qty_available
        result.update({'total_begining': total_begining,
                        'total_internal': total_internal,
                        'total_outgoing': total_outgoing,
                        'total_incoming': total_incoming,
                        'total_end': int(total_end),
                        })
        return result
