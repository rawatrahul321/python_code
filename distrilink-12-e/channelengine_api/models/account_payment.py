# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import api, fields, models, _
from odoo.addons.channelengine_api.models.authorization import AuthorizeChannelEngine
from odoo.exceptions import UserError

class account_payment(models.Model):
    _inherit = 'account.payment'

    def action_validate_invoice_payment(self):
        """ Posts a payment used to pay an invoice. This function only posts the
        payment by default but can be overridden to apply specific post or pre-processing.
        It is called by the "validate" button of the popup window
        triggered on invoice form by the "Register Payment" button.
        """
        if any(len(record.invoice_ids) != 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        res = self.post()
        conns = self.env['channelengine.connection'].search([])
        for record in self:
            if len(record.invoice_ids) == 1:
                if record.invoice_ids.type == 'out_refund' and record.invoice_ids.return_id:
                    if record.invoice_ids.manual_returns:
                        return_lines = []
                        for line in record.invoice_ids.invoice_line_ids:
                            return_lines.append({
                                'MerchantProductNo': line.product_id.marchant_product_no,
                                'Quantity': int(line.quantity),
                            })
                        return_values = {'MerchantOrderNo': record.invoice_ids.marketplace_id,
                            'MerchantReturnNo': record.invoice_ids.marchant_return_no,
                            'Lines': return_lines,
                            'Id': record.invoice_ids.return_id,
                            'Reason': record.invoice_ids.return_reason,
                            'CustomerComment': record.invoice_ids.customer_comment,
                            'MerchantComment': record.invoice_ids.merchant_comment,
                            'RefundInclVat': record.invoice_ids.amount_total,
                            'RefundExclVat': record.invoice_ids.amount_untaxed}
                        for conn in conns:
                            returns = AuthorizeChannelEngine(conn.url, conn.api_key).create_fbm_order_returns(return_values)
                            self.env['audit.log'].put_audit_log('FBM OrderReturn from Odoo to CE',
                                'Success' if returns.get('Success') == True else 'Failed', returns, '')
                    else:
                        lines = []
                        for line in record.invoice_ids.invoice_line_ids:
                            lines.append({
                                'MerchantProductNo': line.product_id.marchant_product_no,
                                'AcceptedQuantity': int(line.quantity),
                                'RejectedQuantity': 0
                            })
                        returnData = {'ReturnId': record.invoice_ids.return_id, "Lines": lines}
                        for conn in conns:
                            returns = AuthorizeChannelEngine(conn.url, conn.api_key).update_return_recieved(returnData)
                            self.env['audit.log'].put_audit_log('Update Return Received from Odoo to CE',
                                'Success' if returns.get('Success') == True else 'Failed', returns, '')
        return res
