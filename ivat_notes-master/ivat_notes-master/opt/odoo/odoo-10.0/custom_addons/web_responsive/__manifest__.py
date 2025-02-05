# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Web Responsive",
    "summary": "It provides a mobile compliant interface for NobleCRM Community "
               "web",
    "version": "11.0.1.0.2",
    "category": "Website",
    "website": "https://laslabs.com/",
    "author": "LasLabs, Tecnativa, NobleCRM Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    'auto_install': True,
    "depends": [
        'web',
    ],
    "data": [
        'views/assets.xml',
        'views/web.xml',
    ],
    'qweb': [
        'static/src/xml/form_view.xml',
        'static/src/xml/navbar.xml',
    ],
}
