# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Email Invoice Bcc',
    'version': '12.0.1.0',
    'license': 'OPL-1',
    'category': 'Tools',
    'sequence': 718,
    'summary': 'This plug-in allows way for a Bcc address in Invoice Message Wizard on Invoice.',
    'description': """
Add support of Bcc address in invoice message for send email popup.
    """,

    'company': 'Caret IT Solutions Pvt. Ltd.',
    'author': 'Anand Shukla, Caret IT Solutions Pvt. Ltd.',
    'maintainer': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'https://www.caretit.com',
    'depends': ['mail', 'mail_compose_bcc'],
    'data': [
        'wizard/account_invoice_send_view.xml',
    ],

    'images': ['static/description/banner.jpg'],
    'price': 8.00,
    'currency': 'EUR',

    'installable': True,
    'auto_install': False,
    'application': True,
}
