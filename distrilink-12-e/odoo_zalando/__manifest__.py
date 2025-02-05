# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Zalando - Odoo Integration',
    'category': 'Sales',
    'sequence': 1,
    'description': """
        Add OrderTypeId in Active Ants using ChannelEngineCountryCode from ChannelEngine and change Invoice Template based on Contry Code.
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.1.0',
    'depends': ['channable_api', 'channelengine_api', 'active_ants_api', 'active_ants_stock_update', 'audit_logs'],
    'data': [
        'security/ir.model.access.csv',
        'views/channelengine_country_code.xml',
        'views/sale_order_view.xml',
        'views/zalando_logo_view.xml',
        'views/report_invoice_layout.xml'
    ],
    'installable': True,
}
