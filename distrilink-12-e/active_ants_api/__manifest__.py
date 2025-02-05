# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Active Ants API',
    'category': 'Sales',
    'sequence': 1,
    'description': """
        Active Ants API Integration, Post order in ACtive Ants and get shipping update and update it in ChannelEngine.
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.1.0',
    'depends': ['channelengine_api', 'audit_logs'],
    'data': [
        'security/ir.model.access.csv',
        'data/active_ants_cron.xml',
        'views/active_ants_view.xml',
        'views/product_view.xml',
        'views/sale_order_view.xml'
    ],
    'installable': True,
}
