# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models, _
from odoo.http import request


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"

    provider = fields.Selection(selection_add=[('cod', 'Cash On Delivery'), ('mod', 'Machine On Delivery')], ondelete='restrict')


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def form_feedback(self, data, acquirer_name):
        super(PaymentTransaction, self).form_feedback(data, acquirer_name)

        tx = None
        # fetch the tx, check its state, confirm the potential SO
        tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
        if hasattr(self, tx_find_method_name):
            tx = getattr(self, tx_find_method_name)(data)
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
        if tx:
        # if tx.acquirer_id.provider == 'cod' and tx.acquirer_id.provider == 'mod':
            order.with_context(send_email=True).action_confirm()

        return True
