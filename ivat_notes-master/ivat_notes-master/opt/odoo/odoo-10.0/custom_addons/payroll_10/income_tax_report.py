from openerp.tools import amount_to_text
from openerp.tools import amount_to_text_en
from openerp.osv import osv
import math
from openerp.report import report_sxw


class income_tax_details_report(report_sxw.rml_parse):    
    def __init__(self, cr, uid, name, context):
        super(income_tax_details_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({'get_tax_lines': self.get_tax_lines,
            
        })
        
    def get_tax_lines(self, obj):
        tax_line = self.pool.get('employee.tds.line')
        res = []
        ids = []
        for id in range(len(obj)):
            if obj[id]:
                ids.append(obj[id].id)
        if ids:
            res = tax_line.browse(self.cr, self.uid, ids)
        return res
    
                       
class wrapped_income_tax_details(osv.AbstractModel):
    _name = 'report.hr_tds.tax'
    _inherit = 'report.abstract_report'
    _template = 'hr_tds.tax'
    _wrapped_report_class = income_tax_details_report