# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Bol Forecast',
    'category': 'Stock',
    'description': """
        Get FBB product Forecast from Bol.com using API and update Reordering Rule to Odoo.
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.1.0',
    'depends': ['stock', 'update_stock_api', 'audit_logs'],
    'data': [
        'data/ir_cron_data.xml',
        'views/bol_api_view.xml'
    ],
    'installable': True,
    "application": False,
}
