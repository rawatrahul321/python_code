# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models
from odoo.tools import pycompat

class FtpShippingFile(models.Model):
    _name = 'ftp.shipping.file'
    _description = 'FRP Shipping FtpShipping File'

    name = fields.Char('File Name')
    shipping_file = fields.Binary('Shipping File', attachment=True)
    status = fields.Selection([
        ('proceed', 'Proceed'),
        ('progress', 'To Be Process')])
    import_date = fields.Datetime('Import Date')
    file_md5 = fields.Char('MD5')
