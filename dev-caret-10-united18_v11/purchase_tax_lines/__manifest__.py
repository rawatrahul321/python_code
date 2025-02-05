# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Purchase Tax Lines',
    'version': '11.0.1.0',
    'category': 'Purchase',
    'sequence': 0,
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': 'Add Purchase Tax lines in purchase order',
    'description': """
Purchase Tax Lines
==================================

This module does add tax lines in purchase order.

    """,
    'depends': ['purchase', 'account'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
