#     "Shree GANESH"
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd. (<http://www.devintellecs.com>).
#
##############################################################################


{
    'name': 'Customize Invoice Format',
    'version': '1.0',
    'sequence':1,
    'category': 'Account',
    'description': """
        App will print New Invocie Format.
    """,
    'author': 'AJAY KHANNA',
    'summary': 'App will print New Invocie Format For Accounts And Delivery Challan.',
    'website': 'http://www.odoo.com/',
    'images': ['images/main_screenshot.jpg'],
    'depends': ['account',"report","base","web",'sale','purchase'],
    'data': [
        'view/account.xml',
        'view/transporter.xml',
        'view/consignee.xml',
        'view/extra.xml',
        'view/inherit_report_invoice.xml',
        'view/inherit_report_deliveryslip.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

