# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.addons.channelengine_api.models.authorization import AuthorizeChannelEngine

logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        if self.picking_type_code == 'outgoing':
            self.ensure_one()
            for move in self.move_ids_without_package:
                move.quantity_done = move.product_uom_qty

            if not self.move_lines and not self.move_line_ids:
                self.env['audit.log'].put_audit_log(
                            'Delivery Validate', 'Failed', '', 'Please add some items to move.')
                raise UserError(_('Please add some items to move.'))

            # If no lots when needed, raise error
            picking_type = self.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                self.env['audit.log'].put_audit_log('Delivery Validate', 'Failed', '',
                    'You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.')
                raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = self.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(
                        lambda line: float_compare(line.qty_done, 0,
                                                   precision_rounding=line.product_uom_id.rounding)
                    )

                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            self.env['audit.log'].put_audit_log('Delivery Validate', 'Failed', '',
                                'You need to supply a Lot/Serial number for product %s.'% product.display_name)
                            raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)

            channable_order_state = []
            if self.sale_id and self.sale_id.channable_order_id and not self.sale_id.is_fbm_order:
                if self.tracking_url and self.tracking_code and self.transporter:
                    lines = []
                    for line in self.sale_id.order_line:
                        lines.append({
                            'MerchantProductNo': line.product_id.marchant_product_no,
                            'Quantity': int(line.product_uom_qty)
                        })
                    tracking_info = {
                        "MerchantShipmentNo": self.sale_id.marketplace_id,
                        "MerchantOrderNo": self.sale_id.marketplace_id,
                        "Lines": lines,
                        "TrackTraceNo": self.tracking_code,
                        "TrackTraceUrl": self.tracking_url,
                        "ReturnTrackTraceNo": self.tracking_code,
                        "Method": self.transporter
                    }
                    conn = self.env['channelengine.connection'].search([])
                    for con in conn:
                        shipment_order = AuthorizeChannelEngine(con.url, con.api_key).create_order_shipment(tracking_info)
                        logger.info(_("Shipping Order Status %s, %s" %(shipment_order, self.sale_id)))
                        self.env['audit.log'].put_audit_log(
                            'Delivery Validate', 'Success' if shipment_order.get('Success') == True else 'Failed',
                            '%s, Sale Order Number: %s'%(shipment_order, self.sale_id.name), '')
                        channable_order_state.append(shipment_order.get('Success'))
                        if True not in channable_order_state and 'already exists' in shipment_order.get('Message'):
                            channable_order_state.append(True)
                else:
                    self.env['audit.log'].put_audit_log(
                            'Delivery Validate', 'Failed', '', 'Please Fill Order Tracking Info Proper')
                    raise UserError(_('Please Fill Order Tracking Info Proper'))

            logger.info(_("Channable Order State ... %s" %(channable_order_state)))
            if True in channable_order_state or self.sale_id.is_empty_shipping or self.sale_id.is_fbm_order or not self.sale_id.channable_order_id:
                if no_quantities_done:
                    view = self.env.ref('stock.view_immediate_transfer')
                    wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
                    return {
                        'name': _('Immediate Transfer?'),
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.immediate.transfer',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': wiz.id,
                        'context': self.env.context,
                    }

                if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
                    view = self.env.ref('stock.view_overprocessed_transfer')
                    wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
                    return {
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'stock.overprocessed.transfer',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': wiz.id,
                        'context': self.env.context,
                    }

                # Check backorder should check for other barcodes
                if self._check_backorder():
                    return self.action_generate_backorder_wizard()
                self.action_done()
                return
        else:
            if self.picking_type_code == 'incoming' and self.sale_id and self.sale_id.channable_order_id:
                for move in self.move_ids_without_package:
                    move.quantity_done = move.product_uom_qty
            return super(StockPicking, self).button_validate()
