# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Update FBB Product Stock',
    'category': 'Stock',
    'description': """
        Get FBB product Stock from Bol.com using API and update stock to Odoo.
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.1.0',
    'depends': ['channable_api', 'audit_logs'],
    'data': [
        'security/ir.model.access.csv',
        'data/stock_cron.xml',
        'views/bol_connection_view.xml'
    ],
    'installable': True,
}
