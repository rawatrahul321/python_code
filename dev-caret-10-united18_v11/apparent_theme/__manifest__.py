# -*- coding: utf-8 -*-
# ToDo: License.

{
    'name': 'Apparent Backend Theme',
    'summary': 'The Theme for Responsive Odoo Backend.',
    'description': '',
    'version': '11.0.1.0',
    'category': 'Theme',
    'website': 'https://www.caretit.com/',
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'license': '',
    'images': [],
    'installable': True,
    'depends': ['web'],
    'data': [
        'views/backend_assets.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/form_view.xml',
        'static/src/xml/navbar.xml',
    ],
}
