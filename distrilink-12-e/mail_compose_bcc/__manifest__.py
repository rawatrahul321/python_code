# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Email Composer Bcc',
    'version': '12.0.1.0',
    'license': 'OPL-1',
    'category': 'Tools',
    'sequence': 718,
    'summary': 'This plug-in allows way for a Bcc address in Composer Message Wizard on Sale Order, Invoice etc.',
    'description': """
Add support of Bcc address in composer message for send email popup.
    """,

    'company': 'Caret IT Solutions Pvt. Ltd.',
    'author': 'Anand Shukla, Caret IT Solutions Pvt. Ltd.',
    'maintainer': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'https://www.caretit.com',
    'depends': ['mail', 'mail_bcc'],
    'data': [
        'views/mail_message.xml',
        'wizard/mail_compose_message_view.xml',
    ],

    'images': ['static/description/banner.jpg'],
    'price': 8.00,
    'currency': 'EUR',

    'installable': True,
    'auto_install': False,
    'application': True,
}
