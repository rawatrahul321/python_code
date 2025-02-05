# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons.channelengine_api.models.authorization import AuthorizeChannelEngine

logger = logging.getLogger(__name__)

class CancelReason(models.TransientModel):
    _name = 'cancel.reason'
    _description = 'Cancel Reason'

    name = fields.Char('Cancel Reason')
    reason_code = fields.Selection([
        ('NOT_IN_STOCK', 'Out Of Stock'),
        ('DAMAGED', 'Damaged'),
        ('INCOMPLETE', 'Incomplete'),
        ('CLIENT_CANCELLED', 'Cancelled after consultation with customer support'),
        ('INVALID_ADDRESS', 'Invalid Address'),
        ('OTHER', 'Other')], default='NOT_IN_STOCK')

    def cancel_order(self):
        conn = self.env['channelengine.connection'].search([])
        for con in conn:
            data_dict = self._context.get('cancel_data')
            data_dict.update({'ReasonCode': self.reason_code, 'Reason': self.name})
            cancel_order = AuthorizeChannelEngine(con.url, con.api_key).update_order_cancellation(data_dict)
            logger.info(_("Cancel_order Orders..., %s" %(cancel_order)))
            self.env['audit.log'].put_audit_log(
                'Cancel Order', 'Success' if cancel_order.get('Success') == True else 'Failed', cancel_order, '')
            if cancel_order.get('Success') == True:
                sale_order = self.env['sale.order'].browse(self._context.get('active_id'))
                if sale_order:
                    sale_order.write({'state': 'cancel'})
            else:
                self.env['audit.log'].put_audit_log(
                    'Cancel Order', 'Failed', '', cancel_order.get('Message'))
                logger.warning(_(cancel_order.get('Message')))
