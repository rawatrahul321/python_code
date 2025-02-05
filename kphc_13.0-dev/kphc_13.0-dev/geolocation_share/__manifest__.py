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
  "name"                 :  "Website Customer Geolocation Address",
  "summary"              :  """Share geolocation on shipping page""",
  "category"             :  "website",
  "version"              :  "2.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Customer-Geolocation-Address.html",
  "description"          :  """This module works very well with latest version of Odoo 12.0
--------------------------------------------------------------""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=geolocation_share",
  "depends"              :  ['website_sale'],
  "data"                 :  ['views/website_templates.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  25,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
  "post_init_hook"       :  "_auto_configuration",
}