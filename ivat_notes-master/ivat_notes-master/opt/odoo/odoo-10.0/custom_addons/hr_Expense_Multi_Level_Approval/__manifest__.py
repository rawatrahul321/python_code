# -*- encoding: utf-8 -*-
# JAI SHREE GANESH
# GNU Affero General Public License <http://www.gnu.org/licenses/>
{
    "name" : "Expense Multi Level Approval",
    "version" : "10.3",
    'license': 'AGPL-3',
    "author" : "AJAY KHANNA",
    "category": "Generic Modules/Human Resources",
    'website': 'http://www.odoo.com/',
    'description': """
    Manage Expense Claims, Authorization and Repayment Processes Easily.
    """,
    'images': ['static/description/icon.png'],
    'depends' : ['hr', 'hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/hr_expense.xml',
        ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
