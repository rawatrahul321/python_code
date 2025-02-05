# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name' : 'Caret United_18',
    'version' : '1.0',
    'category': 'Multi-company configuration',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': 'this module provide basic things for configuration of multi-company environment',
    'description': """
        1) Hide old website menu to all users.
        2) Add Goto Website menu for redirect on website side.
        3) Only Login user can see shop menu on website page.
        4) Hide Translations menu in settins menu for all users.
        5) separate menu created for email in setting menu.
        6) Hide Point of sale tab on User form.
        7) Create new Group for united18 admin.
        8) Only current company customers show and parent company partner show as vendor.
        9) Administration access rights show in user form only when debug mode on. 

        Company Creation Time :
        
        1) Chart of account create.
        2) Create Customer Location and vendor location of company.
        3) Assign parent company locations in customer and vendor location of created company partner.
        4) Use parent company property for Assign Account Receivable and Account Payable in created company partner.
        5) Create other locations like return_location_stock , return_location_vendor , 
        6) Two users created when company created.
        7) Particular fix groups(access rights) assign that two users.
        8) Also set property and location in Partner of users according their company.
        9) Create stock picking type for company.
        10) Create account Journals
        11) POS Config Record for Session Start

    """,
    'depends' : ['account','sale_stock','purchase','point_of_sale','website_sale'],
    'data': [
        'data/sequence.xml',
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'data/stock_data.xml',
        'views/menu_access.xml',
        'views/res_users.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
