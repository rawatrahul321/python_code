# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Kentucky Active Ants API',
    'category': 'Sales',
    'sequence': 1,
    'description': """
        Kentucky Active Ants API Integration, Post order in Kentucky ACtive Ants and get shipping update and update it in ChannelEngine.
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.1.0',
    'depends': [
        'channelengine_api',
        'sales_layer_api',
        'active_ants_api',
        'active_ants_stock_update',
        'audit_logs'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/kentucky_ants_cron.xml',
        'views/product_view.xml',
        'views/kentucky_active_ants_view.xml',
        'views/sale_order_view.xml'
    ],
    'installable': True,
}
