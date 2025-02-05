#     "SHREE GANESHAY NAMAH"
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd. (<http://www.devintellecs.com>).
#
##############################################################################


{
    'name': 'Info Module',
    'version': '1.0',
    'sequence':1,
    'category': 'Manufacturing',
    'description': """
    Info Module For Tracking Work Order During Assembly Line.
    """,
    'author': 'AJAY KHANNA',
    'summary': 'Info Module For tracking Each Activity in Manufacturing.',
    'website': 'http://www.odoo.com/',
    'images': ['images/main_screenshot.jpg'],
    'depends': ["base",'mrp'],
    'data': [
        'views/info_view.xml',
        'security/ir.model.access.csv',
        
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

