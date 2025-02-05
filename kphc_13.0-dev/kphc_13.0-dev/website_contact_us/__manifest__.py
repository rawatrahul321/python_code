# -*- coding: utf-8 -*-

{
    'name': 'Website Contact Us',
    'summary': 'Website Contact Us page',
    'description': 'Website Contact Us page',
    'category': 'Website',
    'version': '12.0.1.0.0',
    'author': 'simplit.me',
    'website': 'http://simplit.me/',
    'depends': ['website', 'crm', 'website_crm'],
    'data': [
        'data/contactus_email_template.xml',
        'data/website_crm_data.xml',
        'views/crm_lead_form_inherit.xml',
        'views/website_form.xml',
        'views/assets.xml'
    ],
    'installable': True,

}
