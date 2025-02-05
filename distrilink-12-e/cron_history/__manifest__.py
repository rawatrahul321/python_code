# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           # 
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

{
    'name' : 'Cron History',
    'version': '12.0.1.0',
    'summary': 'Track Cron History',
    'category': '',
    'description': """ This Module allows you to track cron history. """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'https://www.caretit.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_cron_history_view.xml',
        'views/ir_cron_view.xml',
    ],
    'installable': True,
    'application': False,
}
