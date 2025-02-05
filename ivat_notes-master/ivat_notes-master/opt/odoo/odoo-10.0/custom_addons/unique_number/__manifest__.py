#     "SHREE GANESHAY NAMAH"
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd. (<http://www.devintellecs.com>).
#
##############################################################################


{
    'name': 'Unique Number',
    'version': '1.0',
    'sequence':1,
    'category': 'Stock',
    'description': """
    Unique Serial Number For Tracking Manufacturing Process During Assembly Line.
    """,
    'author': 'AJAY KHANNA',
    'summary': 'Add Unique Serial Number For tracking Each Activity in Manufacturing.',
    'website': 'http://www.odoo.com/',
    'images': ['images/main_screenshot.jpg'],
    'depends': ["base",'stock'],
    'data': [
        'views/stock_unique_number_view.xml',
        'data/unique_serial_data.xml',
        'report/report_unique_no.xml',
        'report/stock_report_view.xml',
        'security/ir.model.access.csv',
        'wizard/auto_generate_unique_no_view.xml',
        
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

