# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name' : 'Caret Product Set Variant',
    'version' : '1.0',
    'category': 'Multi-company configuration',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': 'Add variant management to product set in website.',
    'description': """
    """,
    'depends' : ['sale_product_set_variant', 'website_sale', 'caret_united18_website','website_sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_set_view.xml',
        'views/templates.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
