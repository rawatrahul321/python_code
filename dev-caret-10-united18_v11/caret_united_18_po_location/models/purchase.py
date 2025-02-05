# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # stock_location_id = fields.Many2one('stock.location', string="Stock Location")

    # @api.model
    # def _prepare_picking(self):
    #     res = super(PurchaseOrder, self)._prepare_picking()
    #     if self.stock_location_id:
    #         res['location_dest_id'] = self.stock_location_id.id
    #     return res

    @api.multi
    def _create_invoice(self):
        invoice = self.env['account.invoice'].create({
            'origin': self.name,
            'type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or False,
            'user_id': self.env.user.id,
            'comment': self.notes,
        })

        for orderLine in self.order_line:
            account_id = orderLine.product_id.property_account_income_id.id or orderLine.product_id.categ_id.property_account_income_categ_id.id
            lines = {
                'name': orderLine.product_id.name,
                'origin': self.name,
                'account_id': account_id,
                'invoice_id': invoice.id,
                'price_unit': orderLine.price_unit,
                'quantity': orderLine.product_qty,
                'product_id': orderLine.product_id.id,
                'invoice_line_tax_ids': [(6, 0, orderLine.taxes_id.ids)],
            }
            self.env['account.invoice.line'].create(lines)

        return invoice

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        res.button_confirm()
        invoice = res._create_invoice()
        res.invoice_ids = [(6, 0, [invoice.id])]
        res.invoice_count = len(invoice)
        return res

    @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done','cancel'))
                if not pickings:
                    res = order._prepare_picking()
                    picking = StockPicking.create(res)
                else:
                    picking = pickings[0]
                moves = order.order_line._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)

                if picking.location_dest_id.partner_id and picking.location_dest_id.partner_id.email:
                    emailTemp = self.env.ref('caret_united_18_po_location.receive_product')
                    mailObj = self.env['mail.mail']
                    pickingEmail = emailTemp.generate_email(self.id, fields=None)
                    pickingEmail['email_to'] = picking.location_dest_id.partner_id.email
                    pickingEmail['email_from'] = self.env.user.company_id.email
                    if pickingEmail['email_to'] and pickingEmail['email_from']:
                        mailID = mailObj.create(pickingEmail)
                        if mailID:
                            mailObj.send(mailID)
        return True

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def _create_or_update_picking(self):
        for line in self:
            if line.product_id.type in ('product', 'consu'):
                # Prevent decreasing below received quantity
                if float_compare(line.product_qty, line.qty_received, line.product_uom.rounding) < 0:
                    raise UserError('You cannot decrease the ordered quantity below the received quantity.\n'
                                    'Create a return first.')

                if float_compare(line.product_qty, line.qty_invoiced, line.product_uom.rounding) == -1:
                    # If the quantity is now below the invoiced quantity, create an activity on the vendor bill
                    # inviting the user to create a refund.
                    activity = self.env['mail.activity'].sudo().create({
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'note': _('The quantities on your purchase order indicate less than billed. You should ask for a refund. '),
                        'res_id': line.invoice_lines[0].invoice_id.id,
                        'res_model_id': self.env.ref('account.model_account_invoice').id,
                    })
                    activity._onchange_activity_type_id()

                # If the user increased quantity of existing line or created a new line
                pickings = line.order_id.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel') and x.location_dest_id.usage in ('internal', 'transit'))
                picking = pickings and pickings[0] or False
                if not picking:
                    res = line.order_id._prepare_picking()
                    picking = self.env['stock.picking'].create(res)

                move_vals = line._prepare_stock_moves(picking)
                for move_val in move_vals:
                    self.env['stock.move']\
                        .create(move_val)\
                        ._action_confirm()\
                        ._action_assign()

                if picking.location_dest_id.partner_id and picking.location_dest_id.partner_id.email:
                    emailTemp = self.env.ref('caret_united_18_po_location.receive_product')
                    mailObj = self.env['mail.mail']
                    pickingEmail = emailTemp.generate_email(line.order_id.id, fields=None)
                    pickingEmail['email_to'] = picking.location_dest_id.partner_id.email
                    pickingEmail['email_from'] = self.env.user.company_id.email
                    if pickingEmail['email_to'] and pickingEmail['email_from']:
                        mailID = mailObj.create(pickingEmail)
                        if mailID:
                            mailObj.send(mailID)
