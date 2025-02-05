# || Shree Ganeshay Namah ||
# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Attendance Report',
    "summary": "Employee Wise Attendance Report",
    "version": "1.0",
    "category": "Attendance",
    "website": "http://www.odoo.com/",
    'description': """
Employee Wise Attendance Report"
""",
    'author': "AJAY KHANNA",
    'website': 'http://www.odoo.com',
    'license': 'AGPL-3',
    "depends": [
        'hr_attendance','hr_holidays','hr',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    "data": [
        'views/employee.xml',
        'wizard/employee_wise_report.xml',
        'wizard/attendance_report.xml',
        'wizard/today_attendance_report.xml',
        'wizard/all_employee_report.xml',
        
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
