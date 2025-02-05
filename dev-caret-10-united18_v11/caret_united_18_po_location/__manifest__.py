# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name' : 'Caret United 18 Purchase Location',
    'version' : '1.0',
    'category': 'Multi-company configuration',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': 'this module manage purchase product stock location',
    'description': """
        1) when create purchase order its create incoming shipment on selected location and 
        notify with email to responsible person.
        2) click on Save of Purchase Order Form, create vendor bill(Draft)
    """,
    'depends' : ['purchase'],
    'data': [
        'views/purchase_view.xml',
        'data/email_template.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
