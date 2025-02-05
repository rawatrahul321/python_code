# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Audit Logs',
    'category': 'Sales',
    'sequence': 11,
    'description': """
        Audit Logs of Order Status
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.0.1',
    'depends': ['sale', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/audit_log_view.xml',
        'views/assets.xml'
    ],
    'installable': True,
}
