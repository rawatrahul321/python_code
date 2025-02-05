#     "Shree GANESH"
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd. (<http://www.devintellecs.com>).
#
##############################################################################


{
    'name': 'Customize Picking & Packing',
    'version': '1.0',
    'sequence':1,
    'category': 'Inventory',
    'description': """
        Customized Picking & Packing For MRP.
    """,
    'author': 'AJAY KHANNA',
    'summary': 'To Track Picking For Custom MRP Operations.',
    'website': 'http://www.odoo.com/',
    'images': ['images/main_screenshot.jpg'],
    'depends': ['stock',"report","base","web",'sale','purchase','mrp'],
    'data': [
        'views/custom_picking_view.xml',
        'views/unique_outer_packing_view.xml',
        'views/unique_packing_view.xml',
        'views/picking_info_view.xml',
        'views/custom_packing_view.xml',
        'views/wo_outer_packing_view.xml',
        'wizard/packing_unique_number_view.xml',
        'report/stock_barcode.xml',
        'report/unique_inner_carton.xml',
        'report/unique_outer_carton.xml',
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

