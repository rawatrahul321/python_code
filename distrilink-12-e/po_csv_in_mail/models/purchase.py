# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_rfq_send(self):
        res = super(PurchaseOrder, self).action_rfq_send()
        purchase_order_csv = self.env['purchase.order.csv'].create({'purchase_order_id': self.id})
        csv_attachment = purchase_order_csv.attach_purchase_order_line_csv()
        try:
            if self.env.context.get('send_rfq', False):
                temp_id = self.env.ref('purchase.email_template_edi_purchase')
            else:
                temp_id = self.env.ref('purchase.email_template_edi_purchase_done')
        except ValueError:
            temp_id = False
        if csv_attachment and temp_id:
            temp_id.write({'attachment_ids': [(6, 0, csv_attachment.ids)]})
        return res
