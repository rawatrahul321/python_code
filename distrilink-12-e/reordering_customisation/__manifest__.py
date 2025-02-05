# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Reordering Customisation',
    'category': 'Purchase',
    'description': """
        Run Reordering rule based on recurring date and create RFQ after that date
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.1.0',
    'depends': ['channable_api'],
    'data': [
        'views/stock_warehouse_view.xml'
    ],
    'installable': True,
}
