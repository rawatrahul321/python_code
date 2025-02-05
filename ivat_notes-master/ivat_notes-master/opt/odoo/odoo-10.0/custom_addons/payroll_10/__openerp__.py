
{
    'name': 'Payroll Management ',
    'version': '1.1',
    'category': 'Payroll Management',
    'sequence': 19,
    'summary': 'Payroll Contracts',
    'description': """
Manage Employee Taxation (TDS) Payroll Contracts easily.
=======================================================


    """,
    'author': 'AJAY KHANNA',
    'website': 'https://www.odoo.com/',
    'images': ['static/description/icon.png'],
    'depends': [ 'report','hr_contract','hr_payroll','hr','hr_payroll_account','account_period',
                'account_fiscal_year','date_range','attendance_reminder','hr_attendance_overtime','l10n_in_hr_payroll','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/payroll.xml',
        'views/tax_and_savings.xml',
        'views/income_tax_detail.xml',
        'views/income_tax_report.xml',
        'views/public_holiday.xml',
        'views/hr_holiday_views.xml',
        'views/salary_rule.xml',
        'report/payslip_report.xml',
        
            ],
    'test': [
        
    ],
    'demo': [
       
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
