# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Email Bcc',
    'version': '12.0.1.0',
    'license': 'OPL-1',
    'category': 'Tools',
    'sequence': 717,
    'summary': 'This plug-in allows way for a Bcc address in Email & Templates.',
    'description': """
Add support of Bcc address in email template and send those email to Bcc
address in email. The Bcc email address is not supported by odoo standard.
    """,

    'company': 'Caret IT Solutions Pvt. Ltd.',
    'author': 'Anand Shukla, Caret IT Solutions Pvt. Ltd.',
    'maintainer': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'https://www.caretit.com',
    'depends': ['mail'],
    'data': [
        'views/mail_template_view.xml',
        'views/mail_mail_view.xml',
    ],

    'images': ['static/description/banner.jpg'],
    'price': 9.00,
    'currency': 'EUR',

    'installable': True,
    'auto_install': False,
    'application': True,
}
