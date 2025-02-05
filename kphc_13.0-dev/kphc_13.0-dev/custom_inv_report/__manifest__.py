# -*- coding: utf-8 -*-
{
    'name': "Custom Invoice Report",
    'summary': """
        Custom Invoice Report""",
    'description': """
    - New custom report for Invoices.
    - Account move extended.
    - Account move line sequence from 'account_invoice_line_sequence' module.
    - Amount in word from 'amt_to_word' module.
    """,
    'author': "SimplitME",
    'website': "http://simplit.me",
    'category': 'Report',
    'version': '13.0.0.2',
    'depends': ['account_invoice_line_sequence', 'amt_to_word'],
    'data': [
        'views/cust_invoice_report.xml',
        'views/account_move_views_inherit.xml',
    ],
}
