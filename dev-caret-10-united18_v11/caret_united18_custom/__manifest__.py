# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name' : 'Caret United18 Custom',
    'version' : '1.0',
    'category': 'Multi-company configuration',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': 'This module for simple customization of odoo ERP Backened .',
    'description': """
            1) Hide contacts and addresses tab from customer form view.
            2) Restriction on create and edit purchase order and products for outlet user.
            3) menus and Sub menus :
                1. Hide Invoicing menu in sale menu.
                2. Hide Vendor Bills menu in control menu from purchase menu.
                3. Create new Menu(Bill Receipts) on Top of menus . this menu access from all login users. Two Sub menu create in Bill Receipts menu.
                   1. Sales Payment
                   2. Purchase Payment
                4. Hide Run Scheduler, Reordering Rules ,Configurations menu and it’s sub menu in Inventory menu.
                5. Product Categories menu of Configuration menu ,move it before Products menu in Master Data menu in Inventory menu.
                6. Inventory Adjustments menu in Inventory menu only show that users which have united18 group access.
                7. Create product transfer and create return menu in master data menu of inventory menu.
                8. Invoicing menu Hide from Top of menus.

            4) smart buttons:
                1. Hide smart buttons on sale order form view.
                    - invoices and Transactions smart button.
                    - Create invoice and mark as paid button in header of sale order form.
                2. Hide smart buttons on customer form view:
                    - invoices , vendor bill smart button.
                3. Hide smart buttons on purchase order form view.
                    - Vendor Bill
                4. Hide Buttons in header of Purchase Order for Outlet user.
                    - Re-send RFQ By Email button
                    - Confirm Order button
                    - Cancel button
                5. Hide smart buttons on product form for outlet user.
                    - Reordering Rule
                    - Sales
                    - On Website
                    - Active
                    - Product Move
                6. Add Point Of Sale smart button in product form view.
                7. Hide UPDATE QTY ON HAND button in header of product form for outlet users.

            5) Fields on form view :
                1. Add final sales price field on sale order line, Purchase order line and product page.
                2. Show locations field in customer form without developer mode.
                3. Make Readonly POS Category and eCommerce Categories field on product form.
                4. filter partner and payment journal field in Payment form in Bill Receipt menu.
                5. Hide fields on sale order form view and list view.
                    - Expiration date ,invoice status
                6. Hide fields on purchase order form view.
                    - Incorterm, Payment Term, Billing Status and Approval date.
                7. Hide Fields on product Form
                    - To Weigh With Scale field.
                    - Alternative Products and Accessory Products  fields.
                    - Hide Operation(Buy, Make To Order, Customer lead time) in inventory tab.
                    - Hide Logistics and Traceability options in inventory tab.
                    - Make default value False of company_id field on creation of product
                    - Make default value “show inventory on website and prevent sales if not enough stock “ option in Inventory Availability field in Sales Tab.

            6) Hide Filters :
                - Hide To invoice and Upselling Filters on sale order.
                - Hide waiting Bills and Bills received options from Filter.
            7) Hide Tabs in product form for outlet users :
                - Sales
                - Purchase
                - Inventory
                - Invoicing.
            8) Check Credit Limit :
                - Add credit limit name field in customer form. All child company partner have limited amount assign .that amount show how much amount till that company can buy products from parent company.
                - on confirm button in sale order form check credit limit of partner(customer). if it's greater then his total Sale order amount then only confirmed order.
                - Credit limit amount assign by parent company.
            9) Child Company can pay money to parent company for old transactions through payment creation in purchase payment menu in Bill Receipt menu.
            10) Product Transfer OR Move :
                 - Create new menu for product transfer in Master Data menu in Inventory menu.
                 - In this process source product quantity of specific location(stock)  can be transfer to another product  specific location.
                 - Reduce on hand quantity of source product on specific location ,According transfer quantity value. And update on hand quantity in destination product with create move line .
            11) Generic Return :
                 - outlet user(child company user) can return product to parent company .
            12) Hide Purchase Tab in product form.
            13) In Dashboard of inventory ,hide settings option in kanban view of Dashboard.
            14) Invoice tab name change (invoicing to Taxes) in product form.
            15) Order date move to before expiration date on sale order form view.
            16) POS Category and e-commerce Categories are created when product category created.
            17) when user select product category on product form at that time POS Category and eCommerce categories field filled automatically.
            18) after created sale order ,purchase order also created with same value of sale order.

        """,
    'depends' : ['sale_stock',
                 'stock',
                 'mail',
                 'sale',
                 'sale_management',
                 'purchase',
                 'website_sale',
                 'account_voucher',
                 'point_of_sale',
                 'caret_united_18',
                 'sale_margin',
                 'dev_inv_gst_template_india',
                 'account_voucher',
                 'web_widget_image_download'],
    'data': [
            'security/ir.model.access.csv',
            'security/custom_security.xml',
            'data/sequence.xml',
            'views/sale_order_gst_report_view.xml',
            'data/email_template.xml',
            'report/demo_gst_sale_report.xml',
            'report/product_template_report.xml',
            'report/stock_move_report.xml',
            'wizard/sale_product_category.xml',
            'wizard/sale_order_details.xml',
            'wizard/stock_report_wizard.xml',
            'views/res_partner.xml',
            'views/sale_view.xml',
            'views/purchase_view.xml',
            'views/stock_view.xml',
            'views/acount_invoicing_view.xml',
            'views/product_transfer.xml',
            'views/generic_return_view.xml',
            'report/account_invoice_report.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
