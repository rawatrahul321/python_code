{
    "name": "KNET Payment Acquirer",
    "summary": """Integrating KNET Payment Gateway service with Odoo. The module allows the customers to make payments for their ecommerce orders using KNET Payment Gateway service.""",
    "description": """KNET Payment Gateway Payment Acquirer""",
    "version": "13.0.1.0.0",
    "author": "Boraq-Group",
    "website": "https://boraq-group.com",
    "category": "Ecommerce",
    'license': 'OPL-1',
    "depends": ["payment"],
    "external_dependencies": {
        "python": ["pycryptodomex"]
    },
    "data":  [
        "views/payment_acquirer.xml",
        "views/payment_knet_templates.xml",
        "data/knet_payment_data.xml",
        "data/mail_template.xml",
        "report/sale_order_report_templates.xml",
        "report/report_invoice.xml",
    ],
    "images": ['static/description/banner.gif'],
    "application": True,
    "installable": True,
    "price": 199.0,
    "currency": "EUR",
    "pre_init_hook": "pre_init_check",
    "post_init_hook": "create_missing_journal_for_acquirers"
}
