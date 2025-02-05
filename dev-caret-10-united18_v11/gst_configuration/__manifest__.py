# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name' : 'Caret GST Configuration',
    'version' : '1.0',
    'category': 'Multi-company configuration',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': 'This module is provide GST Configuration of Company',
    'description': """
        Company creation time or after company creation If GSTConfiguration is True then all Vendor Taxes assign on all 
        product If GSTConfiguration is False then all related Vendor Taxes of that company is remove into the all product.
    """,
    'depends' : ['base','product','caret_united_18'],
    'data': [
        'views/gst_configure_view.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
