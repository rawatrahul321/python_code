# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Allure Backend Theme(For Enterprise Edition)',
    'category': "Themes/Backend",
    'version': '1.3',
    'license': 'OPL-1',
    'summary': 'Flexible, Powerful and Fully Responsive Customized Backend Theme with many features(Favorite Bar, Vertical Horizontal Menu Bar, '
               'Night Mode, Tree view of Menu and Sub menu, Fuzzy search for apps, Display density) in Enterprise Edition.',
    'description': """ Flexible, Powerful and Fully Responsive Customized Backend Theme with many features(Favorite Bar,
    Vertical Horizontal Menu Bar, Night Mode, Tree view of Menu and Sub menu, Fuzzy search for apps, Display density).

    allure backend theme
Backend
backend theme
responsive backend theme
responsive frontend theme
responsive web theme
responsive website theme
responsive ecommerce theme

global search
fully responsive
User Interface
Odoo ERP
submenu
main menu
toggle
ui ux
ui & ux
bootstrap
Customized Layouts
Menu bar
Submenu bar
Control Panel
List view
Search option layout
Form view action buttons
Dashboard
Kanban View
List View Form View
Graph View Pivot View
General View
Calendar View
Planner view Chat Panel
variations
color palette
default color panel
color scheme
colour palette
default colour panel
colour scheme
Dynamic Graph view
desktop layout
tablet layout
mobile layout
desktop view
tablet view
mobile view
favourite bar
full width
horizontal tab
vertical tab
normal view
light view
night view
customized icons
2d icon
3d icon
isometric icon
base icon
dynamic color palette
dynamic colour palette
display density
horizontal menu
vertical menu
full screen
default form view
comfortable
compact
allure
flexible
fuzzy search
theme color
theme colour
app icon
without global search

    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'depends': ['web_enterprise'],
    'website': 'www.synconics.com',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/ir_module_views.xml',
        'views/webclient_templates.xml',
        'data/theme_data.xml',
        'views/res_users_views.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'images': [
        'static/description/main_screen.png',
        'static/description/allure_screenshot.png',
    ],
    'post_init_hook': 'post_init_check',
    'price': 649.0,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'bootstrap': True,
    'application': True,
}
