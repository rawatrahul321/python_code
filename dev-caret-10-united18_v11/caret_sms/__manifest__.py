# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name' : 'Caret SMS',
    'version' : '1.0',
    'category': 'SMS',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': 'this module provide facility to send sms using TextLocal',
    'description': """
        -Allows to set credential for TextLocal to send sms
        -Allows Generic view to send sms
        -Allows to send sms when sale, purchase confirmation
        -Allows send sms to customer from res.partner model
    """,
    'depends' : ['sale','purchase','caret_united_18','caret_united18_pos','sms'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/customer_sms_view.xml',
        'views/res_config_settings_views.xml',
        'views/sms.xml',
        'views/sms_body_template.xml',
        'data/data.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
