# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Active Ants Replenish',
    'category': 'Sales',
    'sequence': 1,
    'description': """
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.1.0',
    'depends': ['active_ants_api','purchase_stock', 'wk_wizard_messages', 'audit_logs'],
    'data': [
        'security/ir.model.access.csv',
        'data/stock_mutation_cron.xml',
        'data/purchase_order_email_template.xml',
    ],
    'installable': True,
}
