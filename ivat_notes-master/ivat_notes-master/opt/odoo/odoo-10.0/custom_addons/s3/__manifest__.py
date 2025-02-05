# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "s3 storage",
    "summary": "Manage all kind of date range",
    "version": "10.0.1.0.2",
    "category": "Uncategorized",
    "website": "https://odoo-community.org/",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base", "mail"],

    "data": [
        # "security/ir.model.access.csv",
        # "security/date_range_security.xml",
        "views/smtp_per_user_view.xml",
        # "views/date_range_view.xml",
        # "wizard/date_range_generator.xml",
    ],
    "qweb": [
        # "static/src/xml/date_range.xml",
    ]
}
