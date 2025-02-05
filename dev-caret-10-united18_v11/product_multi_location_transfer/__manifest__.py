# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name' : 'Product Multi-Location Transfer',
    'version' : '11.0.1.0',
    'category': 'Inventory',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': '',
    'description': """

        """,
    'depends' : ['stock', 'caret_united_18'],
    'data': [
            'security/ir.model.access.csv',
            'views/stock_multi_transfer.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
