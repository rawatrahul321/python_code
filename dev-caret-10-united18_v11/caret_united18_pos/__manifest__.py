# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################
{
    'name' : 'Caret United18 POS ',
    'version' : '1.0',
    'category': 'Multi-company configuration',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': '',
    'description': """
    1) Hide all menus except Dashboard, Orders and reporting in POS.
    2) Hide Settings options in Dashboard for All users.
    3) Hide invoice button and Payments tab on POS order form for outlet users.
    4) Show Available Stock on products in pos order process.
    5) Disable(Hide) Price Editing button on pos form.
    6) Final sales price(end user price) use instead of sales price on pos order.
    7) only show current company partners(customer)
    8) Minus Symbol Compulsory in quantity of product in Pos order line after return of pos order.
    9) customer menu show for see customers of company.
    """,
    'depends' : ['point_of_sale','caret_united_18'],
    'data': [
        'security/ir.model.access.csv',
        'data/pos_cron.xml',
        'wizard/pos_order_details.xml',
        'wizard/pos_balance_details.xml',
        'wizard/export_customers.xml',
        'report/pos_balance_report.xml',
        'views/pos.xml',
        'views/templates.xml',
    ],
    'demo': [],
    'qweb': ['static/src/xml/base.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
