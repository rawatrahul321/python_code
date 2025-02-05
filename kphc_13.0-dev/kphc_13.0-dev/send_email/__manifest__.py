# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'KPHC Delivery Notification Development',
    'version': '13.0.0.2',
    'summary': 'KPHC Delivery Notification Development',
    'category': 'Field Service',
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'depends': ['website_sale', 'sale_management', 'mail', 'delivery', 'website_sale_stock'],
    'data': [
        'data/email_temp_delivery.xml',
        'data/payment_acquire_data.xml',
        # 'data/sale_email_template.xml',
        'views/sale_order_views.xml',
        'views/send_an_email.xml',
    ],
    'installable': True, 
    'auto_install': False,
}
