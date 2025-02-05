# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Reminder",
    'version': "1.0",
    'author': "AJAY KHANNA",
    'summary': '''
             This Module to send an Email and SMS to employee if they didn't sign
             in/out on working days.
    ''',
    'desciption':'''
    The module uses scheduled task to execute a function which scans all
    employees and check if they didn't sign in during their work schedule.
    The module also checks if the employee has a valid vacation through HR
    Leaves.

    For the module to work proberly:
     - each employee should have a valid contract.
     - working schedule should be available for each contract.
     - use Leave Management to exclude employee's vacations.

    ''',
    'category': "hr",
    'data': [
        'attendance_reminder_cron.xml',
       # 'edi/attendance_reminder_action_data.xml',
    ],
    'license': 'AGPL-3',
    'website': 'http://www.odoo.com',
    'depends': ['hr'],
    'installable': True,
    'auto_install': False
}
