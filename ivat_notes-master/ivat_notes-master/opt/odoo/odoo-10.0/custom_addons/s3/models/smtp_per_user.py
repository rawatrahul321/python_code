# -*- coding: utf-8 -*-

# from odoo import odoo, fields
from odoo import models,fields

# from . import s3_helper
from odoo import api


from email.utils import parseaddr, formataddr

class ir_mail_server(models.Model):
    _inherit = "ir.mail_server"

    user_id = fields.Many2one('res.users', string="Owner")
    email_name = fields.Char('Email Name', help="Overrides default email name")
    force_use = fields.Boolean('Force Use', help="If checked and this server is chosen to send mail message, It will ignore owners mail server")

    @api.model
    def replace_email_name(self, old_email):
        """
        Replaces email name if new one is provided
        """
        if self.email_name:
            old_name, email = parseaddr(old_email)
            return formataddr((self.email_name, email))
        else:
            return old_email

class mail_mail(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        ir_mail_server_obj = self.env['ir.mail_server']
        res_user_obj = self.env['res.users']
        for email in self:
            if not email.mail_server_id.force_use:
                user = res_user_obj.search([('partner_id', '=', email.author_id.id)], limit=1)
                if user:
                    mail_server = ir_mail_server_obj.search([('user_id', '=', user.id)], limit=1)
                    if mail_server:
                        email.mail_server_id = mail_server.id
            email.email_from = email.mail_server_id.replace_email_name(email.email_from)
        return super(mail_mail, self).send(auto_commit=False, raise_exception=False)
# class ir_mail_server(models.Model):
#     _inherit = "ir.mail_server"
#
#     user_id = fields.Many2one('res.users', string="Owner")
#     def send(self,auto_commit=False, recipient_ids=None, context=None):
#         print("------------------------------",recipient_ids,context,self.create_uid)
#
#         server_id = self.env['ir.mail_server'].search([('user_id','=',self.create_uid.id)])
#         print("---------------------------sel",server_id,server_id.create_uid.id)
#         # server_id = server_id[0] or False
#         # print("-----------------------------server_id",server_id)
#         # if server_id:
#         self.write({'mail_server_id': server_id.create_uid.id})
#         return super(mail_mail, self).send(auto_commit=auto_commit, recipient_ids=recipient_ids, context=context)
#
#
#
# class mail_mail(models.Model):
#     _inherit = "mail.mail"
