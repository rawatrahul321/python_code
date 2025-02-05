# -*- coding: utf-8 -*-
{
    'name': 'Amount to Word',
    'version': '13.0.0.5',
    'summary': 'Amount to Word on Invoice , sales and Purchase',
    'author': 'Simplit Me - Djay',
    'description': """
    Amount to Word on Invoice
    """,
    'data': [
        'views/amt_to_word_views.xml',
    ],
    'depends': [
        # 'sale',
        # 'purchase',
        'account',
    ],
    'installable': True,
    'application': True,
}
