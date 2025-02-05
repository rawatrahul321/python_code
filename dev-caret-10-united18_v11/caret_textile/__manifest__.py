# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name' : 'Caret United18 Production',
    'version' : '1.0',
    'category': 'MRP',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': 'Huge Level of Customization for Manufacturing order for Textile Industry',
    'description': """
	
    """,
    'depends' : ['product','stock','portal','purchase','account'],
    'data': [
        'security/production_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/data.xml',
        'views/menu_view.xml',
        'views/accessory_view.xml',
        'views/inward_material_view.xml',
        'wizard/finishing_export_report_wizard.xml',
        'views/production_process_view.xml',
        'views/stitching_order_view.xml',
        'views/washing_view.xml',
        'views/finishing_view.xml',
        'views/templates.xml',
        'report/finishing_report_view.xml',
    ],
    'demo': [],
    'qweb': ['static/src/xml/production.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
