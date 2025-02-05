# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'ChannelEngine API',
    'category': 'Sales',
    'sequence': 1,
    'description': """
        ChannelEnging API Integration, Get orders from channelegine to odoo and update status on channelengine.
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.1.3',
    'depends': ['sale_management','stock', 'cron_history', 'channable_api', 'audit_logs'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/channelengine_cron.xml',
        'views/account_invoice_view.xml',
        'views/product_view.xml',
        'wizard/cancel_reason_view.xml',
        'views/channable_api_view.xml',
        'views/res_partner_view.xml',
        'views/channelengine_connection_view.xml',
        'views/stock_picking_view.xml'
    ],
    'installable': True,
}
