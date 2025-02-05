# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Knet Payment Gateway',
    'version': '13.0.1.0.0',
    'summary': 'Knet Payment Gateway',
    #'sequence': 30,
    'description': """
Knet Payment Gateway
====================
Knet Payment Gateway
    """,
    'category': 'Payment',
    'website': '',
    'depends': ['website_sale', 'payment'],
    'data': [
        'views/knet_template_views.xml',
        'data/knet_payment_data.xml',
        'views/website_knet_payment_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
