# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Sales Layer API',
    'category': 'Sales',
    'sequence': 1,
    'description': """
        Sales Layer API Integration
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.1.1',
    'depends': ['channable_api', 'active_ants_api', 'audit_logs'],
    'data': [
        'security/ir.model.access.csv',
        'data/saleslayer_cron.xml',
        'views/sales_layer_connection_view.xml'
    ],
    'installable': True,
}
