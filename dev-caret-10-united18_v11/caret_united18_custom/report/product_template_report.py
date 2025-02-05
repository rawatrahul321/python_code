# -*- coding: utf-8 -*-
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from io import BytesIO

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class ReportAction(models.Model):
    _inherit = 'ir.actions.report'

    report_type = fields.Selection(selection_add=[("xlsx", "xlsx")])

    @api.model
    def render_xlsx(self, docids, data):
        report_model_name = 'report.%s' % self.report_name
        report_model = self.env.get(report_model_name)
        if report_model is None:
            raise UserError(_('%s model was not found' % report_model_name))
        return report_model.with_context({
            'active_model': self.model
        }).create_xlsx_report(docids, data)

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(ReportAction, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env['ir.actions.report']
        qwebtypes = ['xlsx']
        conditions = [('report_type', 'in', qwebtypes),
                      ('report_name', '=', report_name)]
        context = self.env['res.users'].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)


class ReportXlsxAbstract(models.AbstractModel):
    _name = 'report.caret_united18_custom.abstract'

    def create_xlsx_report(self, docids, data):
        objs = self.env[self.env.context.get('active_model')].browse(docids)
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data, self.get_workbook_options())
        self.generate_xlsx_report(workbook, data, objs)
        workbook.close()
        file_data.seek(0)
        return file_data.read(), 'xlsx'

    def get_workbook_options(self):
        return {}

    def generate_xlsx_report(self, workbook, data, objs):
        raise NotImplementedError()

class PartnerXlsx(models.AbstractModel):
    _name = 'report.caret_united18_custom.product_xlsx'
    _inherit = 'report.caret_united18_custom.abstract'

    def generate_xlsx_report(self, workbook, data, products):
        sheet = workbook.add_worksheet('Report')
        bold = workbook.add_format({'bold': True,'align' :'center', 'valign' : 'vcenter'})
        center = workbook.add_format({'align' :'center', 'valign' : 'vcenter'})

        merge_format = workbook.add_format({
                                            'bold':    True,
                                            'border':   3,
                                            'align':    'center',
                                            'valign':   'vcenter',
                                            'fg_color': '#D7E4BC',
                                        })
        sheet.set_column(1, 0, 20)
        sheet.set_column(1, 1, 20)
        sheet.set_column(1, 2, 20)
        sheet.set_column(1, 3, 20)
        sheet.merge_range('A1:B1', 'Available Product Report', merge_format)
        sheet.write(2, 0, 'Product Name', bold)
        sheet.write(2, 1, 'Available Stock', bold)
        sheet.write(2, 2, 'Sales Price', bold)
        sheet.write(2, 3, 'Total Amount', bold)

        row = 3
        for obj in products:
            if obj.qty_available > 0:
                sheet.write(row, 0, obj.name, center)
                sheet.write(row, 1, obj.qty_available, center)
                sheet.write(row, 2, obj.list_price, center)
                sheet.write(row, 3, obj.list_price * obj.qty_available, center)
                row = row + 1