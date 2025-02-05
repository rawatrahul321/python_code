# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.iap.models import iap

_logger = logging.getLogger(__name__)

class CustomerSMS(models.TransientModel):
    ''' send direct sms to customer from res.partner model'''
    _name = 'customer.sms'

    def _default_partner_ids(self):
        partner_ids = self._context.get('active_model') == 'res.partner' and self._context.get('active_ids') or []
        return partner_ids

    partner_ids = fields.Many2many('res.partner', string='Recipients', default=_default_partner_ids, required=True)
    message = fields.Text('Message', required=True)


    @api.multi
    def action_customer_sms(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param('caret_sms.textlocal_api_key')
        sender = self.env['ir.config_parameter'].sudo().get_param('caret_sms.sender')
        to_number = ''
        for partner in self.partner_ids:
            to_mobile = partner.mobile or partner.phone
            if to_mobile:
                if len(to_mobile) == 10:
                    to_number = str(91) + to_mobile
                elif '+' in to_mobile and len(to_mobile) == 13:
                    to_number = to_mobile.replace('+','').strip()
                elif '+' in to_mobile and len(to_mobile) == 11:
                    to_number = to_mobile.replace('+','').strip()
                elif '+' in to_mobile and len(to_mobile) == 11:
                    to_number = to_mobile.replace('+','').strip()
                else:
                    to_number = partner.mobile or partner.phone
                SMS_record = self.env['sms.sms'].sudo().create({'textlocal_api_key':api_key,
                                            'to_number': to_number,
                                            'message': self.message or '',
                                            'sender': sender,
                                            'res_id': partner.id or False,
                                            'res_model': 'res.partner',
                                            })
                SMS_record.sendSMS()
        return True