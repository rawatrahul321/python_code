# -*- coding: utf-8 -*-
{
    "name":  "Website Shipping Address",
    "summary":  "Website Shipping Address.",
    "category":  "Website",
    "version":  "13.0.1.0.0",
    "sequence":  1,
    "author":  "",
    "website":  "",
    "description":  "Changed by djay-12/11/2019",
    "depends":  ['website_sale', 'contacts','base_address_city', 'theme_clarico_vega'],
    "data":  [
            'security/ir.model.access.csv',
            'views/website_shipping_page.xml',
            'views/portal_account_detail.xml',
            'views/views.xml',
            ],
    "application":  True,
    "installable": True,
    "auto_install":  False,
}
