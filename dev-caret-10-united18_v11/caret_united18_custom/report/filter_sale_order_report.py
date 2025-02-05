# -*- coding: utf-8 -*-
import logging
from dateutil import parser
from datetime import datetime
from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class ReportSaleOrder(models.AbstractModel):
    """ sale order report filter by product category """
    _name = 'report.caret_united18_custom.gst_sale_template_report_id'

    @api.multi
    def get_report_values(self, docids, data=None):
        categ = None
        order_lines = []
        if docids:
            docs = self.env['sale.order'].browse(docids)
        if data and data.get('orders'):
            docs = self.env['sale.order'].browse(data.get('orders'))
            categ = data.get('category')
            order_lines = self.env['sale.order.line'].browse(data.get('order_lines'))
        return {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'categories': categ,
            'order_lines': order_lines
        }