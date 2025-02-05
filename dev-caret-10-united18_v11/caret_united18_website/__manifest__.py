# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name' : 'Caret United18 Website',
    'version': '1.0',
    'category': 'Multi-company configuration',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': '',
    'description': """
        This module handle all Website related work.

        1) Show end user price(final sales price) on product form on website product page.
        2) Remove this(30-day money-back guarantee) paragraph from website product page.
        3) Skip payment option on website sale order process.
        4) Create Requests for quotation line in My account from website.
        5) Add note field on website for add some description or queries related order.
            - This note field add on address form in sale order process after adding note .it’s save and show on sale order form view.
        6) show Requests for Quotation in my account menu from  website side. Login User can see only own company RFQ and Purchase order  from website side.it’s filtered by company of current login user
    """,
    'depends' : ['website_sale','caret_united18_custom'],
    'data': [
#         'security/ir.model.access.csv',
        'views/templates.xml',
        'views/res_config_settings.xml',
    ],
    'demo': [],
    'qweb': ['static/src/xml/base.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
