# -*- coding: utf-8 -*-
{
    'name': "Nornoyau Website Font Changes",

    'summary': """
        This module adds Cairo font family to website assets and adds to website body as default.""",

    'description': """
        Introduces new fonts to the website.
    """,

    'author': "",
    'website': "",

    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website','web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
    ],
    # 'images': ['static/description/icon.png'],
    'installable': True,
}
