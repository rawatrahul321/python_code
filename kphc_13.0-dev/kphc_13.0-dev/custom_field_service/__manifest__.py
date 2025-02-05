# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

{
    'name': 'KPHC Custom Report',
    'version': '13.0.1.1',
    'summary': 'KPHC Custom Report',
    'category': 'Field Service',
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'depends': ['industry_fsm_report', 'product', 'project_enterprise', 'uom', 'sale_timesheet', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'data/fsm_report_demo.xml',
        'data/technical_crew_demo.xml',
        'data/service_report_template.xml',
        'data/recommendations_data.xml',
        'data/find_and_remark_data.xml',
        'data/ingredient_product_demo.xml',
        'data/ingredient_uom_demo.xml',
        'views/assets.xml',
        'views/project_task_form_in.xml',
        # 'views/worksheet_template.xml',
        'views/report.xml',
        'reports/service_custom_footer.xml',
        'reports/delivery_report_header_footer.xml',
        'reports/service_report.xml',
        'reports/delivery_report.xml',
        'reports/delivery_report_paper_format.xml',
        'views/service_report_template.xml',
        'views/res_users_in.xml',        
        'views/ingredient_product_view.xml',
        'views/ingredient_uom_view.xml',
    ],
    'installable': True, 
    'auto_install': False,
}
