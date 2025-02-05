# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('channable_order', 'ChannelEngine Order'),
        ('sent', 'Quotation Sent'),
        ('review', 'Error Order'),
        ('vendor_process', 'Vendor Process'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')

    @api.multi
    def action_cancel(self):
        if self.channable_order_id:
            lines = []
            for line in self.order_line:
                lines.append({
                    'MerchantProductNo': line.product_id.marchant_product_no,
                    'Quantity': line.product_uom_qty})
            cancel_data = {
                'MerchantCancellationNo': self.marketplace_id,
                'MerchantOrderNo': self.marketplace_id,
                'Lines': lines,
            }
            ctx = dict(self._context)
            ctx.update({'cancel_data': cancel_data})
            return {
                'name': _('Cancel Reason'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'cancel.reason',
                'views': [(False, 'form')],
                'target': 'new',
                'context': ctx,
            }
        else:
            return super(SaleOrder, self).action_cancel()
