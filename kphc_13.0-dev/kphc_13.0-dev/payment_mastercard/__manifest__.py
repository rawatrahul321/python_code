# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Website Mastercard [Migs] Payment Acquirer",
  "summary"              :  """The module integrates Odoo with MasterCard Internet Gateway Service (MIGS). The customers can then pay for their orders online using the MIGS payment Gateway on Odoo website.""",
  "category"             :  "Website",
  "version"              :  "1.1.1",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Prakash Kumar",
  "website"              :  "https://store.webkul.com/Odoo-Website-MiGS-Payment-Acquirer.html",
  "description"          :  """Odoo Website MasterCard [MiGS] Payment Acquirer
Odoo with MasterCard Internet Gateway Service (MIGS) Payment Acquirer
Odoo MIGS Payment Gateway
Payment Gateway
MasterCard Payment Gateway
Master Card
MasterCard
MasterCard (MIGS)
MasterCard MIGS
MasterCard integration
MIGS Integration
Payment acquirer
Payment processing
Payment processor
Website payments
Sale orders payment
Customer payment
Integrate MasterCard payment acquirer in Odoo
Integrate MIGS payment gateway in Odoo""",
  "depends"              :  ['website_sale_management'],
  "data"                 :  [
                             'views/mastercard.xml',
                             'views/payment_acquirer.xml',
                             'data/mastercard.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  99.0,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}