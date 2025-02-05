# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'FTP Import',
    'category': 'Sales',
    'sequence': 1,
    'description': """
        Channable API Integration
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'http://www.caretit.com',
    'version': '12.0.1.0',
    'depends': ['sale_management','stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/ftp_import_wizard.xml'
        
    ],
    'installable': True,
}
