# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models, _
import urllib.request
import urllib.parse
import ast
import re
class SmsSms(models.Model):
    _name = "sms.sms"
    _description = 'SMS Templates'
    _rec_name = 'to_number'


    textlocal_api_key = fields.Char(string='API Key',help='Textlocal API key you can get it from https://control.textlocal.in/settings/apikeys/')
    sender = fields.Char(string="Sender",default="TXTLCL",help="Use this field to specify the sender name for your message.\
        This must be at least 3 characters in length but no longer than 11 alphanumeric characters or 13 numeric characters.\
        If this is excluded it will use the default sender name configured on your account")
    message = fields.Text(string="Message",required=True, translate=True, sanitize=False,size=765, help="The message content.\
         This parameter should be no longer than 765 characters")
    to_number = fields.Char(string="To Number",required=True)
    group_id = fields.Char(string="Group")
    res_id = fields.Integer(string="Related Document ID")
    res_model = fields.Char(string="Related Document Model")
    simple_reply = fields.Boolean(string="Simply Reply", help="Set to true to enable the Simple Reply Service for \
        the message. This will override any sender value, as a Simple Reply Service number will be used instead.")
    state = fields.Selection([
            ('draft','Draft'),
            ('sent', 'Sent'),
            ('fail', 'Failed')], string="Status", default="draft")

    def sendSMS(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param('caret_sms.textlocal_api_key')
        if not api_key:
            raise UserError(_('Please Set API Key of your TextLocal Account From SMS > SMS Settings'))
        data =  urllib.parse.urlencode({'apikey': api_key, 
                                        'numbers': self.to_number,
                                        'message' : self.message, 
                                        'sender': self.sender,
                                       })
        data = data.encode('utf-8')
        request = urllib.request.Request("https://api.textlocal.in/send/?")
        f = urllib.request.urlopen(request, data)
        fr = f.read()
        fro = fr.decode('utf-8')
        val = ast.literal_eval(fro)
        print ("valssssssssssssss",val)
        if val.get('errors'):
            for i in val.get('errors'):
                if i.get('code') == 3:
                    raise UserError(_('Please Set Valid API Key of Your TextLocal Account'))
                if i.get('code') == 7:
                    raise UserError(_('You have Insufficient credits to send sms from Your Textlocal Account'))
        if val.get('status') == 'success':
            self.state = 'sent'
        elif val.get('status') == 'failure':
            self.state = 'fail'
        return True
