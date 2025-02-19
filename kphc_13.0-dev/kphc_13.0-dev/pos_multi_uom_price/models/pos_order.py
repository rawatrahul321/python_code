# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    uom_id = fields.Many2one('uom.uom')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # def create_picking(self):
    #     """Create a picking for each order and validate it."""
    #     Picking = self.env['stock.picking']
    #     Move = self.env['stock.move']
    #     StockWarehouse = self.env['stock.warehouse']
    #     for order in self:
    #         if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
    #             continue
    #         address = order.partner_id.address_get(['delivery']) or {}
    #         picking_type = order.picking_type_id
    #         return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
    #         order_picking = Picking
    #         return_picking = Picking
    #         moves = Move
    #         location_id = picking_type.default_location_src_id.id
    #         if order.partner_id:
    #             destination_id = order.partner_id.property_stock_customer.id
    #         else:
    #             if (not picking_type) or (not picking_type.default_location_dest_id):
    #                 customerloc, supplierloc = StockWarehouse._get_partner_locations()
    #                 destination_id = customerloc.id
    #             else:
    #                 destination_id = picking_type.default_location_dest_id.id
    #
    #         if picking_type:
    #             message = _(
    #                 "This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (
    #                           order.id, order.name)
    #             picking_vals = {
    #                 'origin': order.name,
    #                 'partner_id': address.get('delivery', False),
    #                 'date_done': order.date_order,
    #                 'picking_type_id': picking_type.id,
    #                 'company_id': order.company_id.id,
    #                 'move_type': 'direct',
    #                 'note': order.note or "",
    #                 'location_id': location_id,
    #                 'location_dest_id': destination_id,
    #             }
    #             pos_qty = any([x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
    #             if pos_qty:
    #                 order_picking = Picking.create(picking_vals.copy())
    #                 order_picking.message_post(body=message)
    #             neg_qty = any([x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
    #             if neg_qty:
    #                 return_vals = picking_vals.copy()
    #                 return_vals.update({
    #                     'location_id': destination_id,
    #                     'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
    #                     'picking_type_id': return_pick_type.id
    #                 })
    #                 return_picking = Picking.create(return_vals)
    #                 return_picking.message_post(body=message)
    #
    #         for line in order.lines.filtered(
    #                 lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty,
    #                                                                                           precision_rounding=l.product_id.uom_id.rounding)):
    #             moves |= Move.create({
    #                 'name': line.name,
    #                 'product_uom': line.uom_id.id,
    #                 'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
    #                 'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
    #                 'product_id': line.product_id.id,
    #                 'product_uom_qty': abs(line.qty),
    #                 'state': 'draft',
    #                 'location_id': location_id if line.qty >= 0 else destination_id,
    #                 'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
    #             })
    #
    #         # prefer associating the regular order picking, not the return
    #         order.write({'picking_id': order_picking.id or return_picking.id})
    #
    #         if return_picking:
    #             order._force_picking_done(return_picking)
    #         if order_picking:
    #             order._force_picking_done(order_picking)
    #
    #         # when the pos.config has no picking_type_id set only the moves will be created
    #         if moves and not return_picking and not order_picking:
    #             moves._action_assign()
    #             moves.filtered(lambda m: m.product_id.tracking == 'none')._action_done()
    #
    #     return True

    def _action_create_invoice_line(self, line=False, invoice_id=False):
        InvoiceLine = self.env['account.invoice.line']
        inv_name = line.product_id.name_get()[0][1]
        # For set uom_id on the invoice. Otherwise, It will taken default one from products.
        inv_line = {
            'invoice_id': invoice_id,
            'product_id': line.product_id.id,
            'quantity': line.qty if self.amount_total >= 0 else -line.qty,
            'uom_id': line.uom_id.id,
            'account_analytic_id': self._prepare_analytic_account(line),
            'name': inv_name,
        }
        # Oldlin trick
        invoice_line = InvoiceLine.sudo().new(inv_line)
        invoice_line._onchange_product_id()
        invoice_line.invoice_line_tax_ids = [(6, False, line.tax_ids_after_fiscal_position.filtered(
            lambda t: t.company_id.id == line.order_id.company_id.id).ids)]
        # We convert a new id object back to a dictionary to write to
        # bridge between old and new api
        inv_line = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
        inv_line.update(price_unit=line.price_unit, discount=line.discount)
        return InvoiceLine.sudo().create(inv_line)
