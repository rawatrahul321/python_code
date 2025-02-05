# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           # 
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

{
    'name' : 'Cron Fail Email',
    'version': '12.0.1.0',
    'summary': 'Send Mail When Cron Process Fail',
    'category': '',
    'description': """ This Module allows you to Send Mail when Cron Process is Failed. """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'https://www.caretit.com',
    'depends': ['base', 'cron_history', 'mail'],
    'data': [
        'data/cron_email_template.xml',
    ],
    'installable': True,
    'application': False,
}
