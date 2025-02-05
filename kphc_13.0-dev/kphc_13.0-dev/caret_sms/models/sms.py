# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################


import ast
import re
import requests

from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models, _


class SmsSms(models.Model):
    _name = "kphc.sms"
    _description = 'SMS Templates'
    _rec_name = 'to_number'

    sender = fields.Char(string="Sender",default="TEST",help="Use this field to specify the sender name for your message.\
        This must be at least 3 characters in length but no longer than 11 alphanumeric characters or 13 numeric characters.\
        If this is excluded it will use the default sender name configured on your account")
    message = fields.Text(string="Message", required=True, translate=True, sanitize=False,size=765, help="The message content.\
         This parameter should be no longer than 765 characters")
    to_number = fields.Char(string="To Number", required=True)
    res_id = fields.Integer(string="Related Document ID")
    res_model = fields.Char(string="Related Document Model")
    state = fields.Selection([
            ('draft','Draft'),
            ('sent', 'Sent'),
            ('fail', 'Failed')], string="Status", default="draft")
    language = fields.Selection([
            ('1','English'),
            ('2', 'Arabic'),
            ('3', 'Unicode')], string="Language", default="1")
    response_log = fields.Text(string="Response", help="Reponse Log for Success or Failure")
    
    def sendSMS(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param('caret_sms.kphc_api_key')
        sender = self.env['ir.config_parameter'].sudo().get_param('caret_sms.sender')
        if not api_key:
            raise UserError(_('Please Set API Key of your TextLocal Account From SMS > SMS Settings'))
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}
        url = "https://api-server14.com/api/send.aspx?"+'apikey='+api_key+'&language='+ \
        self.language+'&sender='+sender+'&mobile='+self.to_number+'&message='+self.message
        r=requests.get(url, headers=hdr)
        status = r.text
        if 'OK' in status:
        	self.state = 'sent'
        	self.response_log = status
        else:
        	self.state = 'fail'
        	self.response_log = status
        return True
