# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################
{
    'name': 'POS Order Display',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Display POS orders in a list',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'depends': ['point_of_sale', 'order_reprinting_pos', 'product_return_pos'],
    'data': ['views/template.xml',],
    'qweb': ['static/src/xml/pos.xml'],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'auto_install': False,
}
