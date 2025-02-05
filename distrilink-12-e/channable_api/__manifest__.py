# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Channable API',
    'category': 'Sales',
    'sequence': 1,
    'description': """
        Channable API Integration
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.5.0',
    'depends': ['sale_management','stock', 'cron_history', 'purchase', 'audit_logs'],
    'data': [
        'security/ir.model.access.csv',
        'data/warehouse_data.xml',
        'data/channable_cron.xml',
        'data/email_template.xml',
        'views/api_view.xml',
        'views/stock_picking_view.xml',
        'views/product_view.xml',
        'wizard/channable_product_import.xml',
        'views/order_view.xml',
        'views/report_invoice_layout.xml',
        'views/ftp_connection_view.xml',
        'views/ftp_shipping_file.xml',
        'views/res_users_view.xml',
        'views/account_invoice_view.xml',
        'views/account_journal_view.xml',
        'views/report_purchase_layout.xml',
    ],
    'installable': True,
}
