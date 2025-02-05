# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################


from odoo import models, fields, api
from ftplib import FTP


class FTPImport(models.TransientModel):
    _name = 'ftp.import'
    description = fields.Text('Description', readonly=True)

    def read_ftp_data(self):
        ftp = FTP('test.rebex.net','demo','password')
        filematch = 'readme.txt'
        def handle_binary(vals):
            self.description = vals
        resp = ftp.retrbinary('RETR %s' % filematch, handle_binary)
        return {
            'name':'FTP Import',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ftp.import',
            'res_id': self.id,
            'view_id': False,
            'target' : 'new'
        }