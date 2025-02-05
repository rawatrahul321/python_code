# -*- coding: utf-8 -*-
{
    'name': "Real-time Biometric Machine Attendance",

    'summary': """
        This module extends the feature of attendance module to
        save real time attendance data from machine. 
        """,

    'description': """
        
    """,

    'author': "Ajay Khanna",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','hr_attendance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
