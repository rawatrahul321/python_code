#     "Shree GANESHAY NAMAH"
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd. (<http://www.devintellecs.com>).
#
##############################################################################


{
    'name': 'Order Form',
    'version': '1.0',
    'sequence':1,
    'category': 'Website',
    'description': """
        Add Orders and quotation in the frontend portal.
    """,
    'author': 'AJAY KHANNA',
    'summary': 'Add Orders and Quotation in the frontend portal',
    'website': 'http://www.odoo.com/',
    'images': ['images/main_screenshot.jpg'],
    'depends': ["base","sale",'stock','mrp'],
    'data': [
        'data/order_data.xml',
        'security/ir.model.access.csv',
        'security/order_form_security.xml',
        'view/order_form_view.xml',
        'view/order_seq.xml',
        'view/portal_inherit.xml',
        'view/rejection.xml',
        'wizard/consolidate_rejection_report.xml',
        'wizard/rework_view.xml',
        'wizard/carton_label.xml',
        'view/inner_carton.xml',
        'view/outer_carton.xml',
        'view/sale_inherit_view.xml',
        'view/update_qty_view.xml',
#         'view/order_form_template.xml',
        
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

