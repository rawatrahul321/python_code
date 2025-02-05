# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Active Ants Sync Stock',
    'category': 'Sales',
    'description': """Get stock via Active Ants API""",
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.1.0',
    'depends': ['active_ants_replenish'],
    'data': [
        'data/stock_update_cron.xml',
    ],
    'installable': True,
}
