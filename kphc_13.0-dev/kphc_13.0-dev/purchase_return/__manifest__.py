# -*- coding: utf-8 -*-
{
    'name': "Return Purchase Order",

    'author': "SimplitME",
    'website': "http://simplit.me/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase',"account","stock"],

    # always loaded
    'data': [
        # 'security/return_security.xml',
        'security/ir.model.access.csv',
        'data/return_data.xml',
        'views/return_views.xml',
        # 'views/account_invoice_views.xml',
        'views/stock_views.xml',
    ],
}
