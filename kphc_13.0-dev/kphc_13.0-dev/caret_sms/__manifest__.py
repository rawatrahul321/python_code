# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name' : 'Caret SMS',
    'version' : '13.0.0.0.1',
    'category': 'SMS',
    'author': 'Caret IT Solutions Pvt. Ltd',
    'website': 'http://www.caretit.com',
    'summary': 'this module provide facility to send sms using KPHC API',
    'description': """
        -Allows to set credential for KPHC to send sms
        -Allows Generic view to send sms
        -Allows to send sms when sale, purchase confirmation
    """,
    'depends' : ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/sale_email_template.xml',
        'views/res_config_settings_views.xml',
        'views/sms.xml',
        'views/sms_body_template.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
