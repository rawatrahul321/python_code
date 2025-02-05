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

logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tracking_url = fields.Char('Shipment URL')
    tracking_code = fields.Char('Tracking Code')
    transporter = fields.Char('transporter')
    is_delivery_not_validated = fields.Boolean('Is Delivery Not Validated')

    @api.multi
    def action_shipment_url(self):
        '''
        redirect page on Url
        '''
        return {
            'name': _("Shipment URL"),
            'type': 'ir.actions.act_url',
            'url': self.tracking_url,
            'target': 'new',
        }


    @api.multi
    def button_validate(self):
        if self.picking_type_code == 'outgoing':
            self.ensure_one()
            for move in self.move_ids_without_package:
                move.quantity_done = move.product_uom_qty

            if not self.move_lines and not self.move_line_ids:
                raise UserError(_('Please add some items to move.'))

            # If no lots when needed, raise error
            picking_type = self.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits
                ) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(float_is_zero(
                move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done.\
                 To force the transfer,switch in edit more and encode the done quantities.'))

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
                            raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)

            channable_order_state = ''
            if self.sale_id and self.sale_id.channable_order_id and not self.sale_id.is_fbm_order:
                if self.tracking_url and self.tracking_code and self.transporter:
                    conn = self.env['channable.connection'].search([('api_project_id', '=', self.sale_id.channable_project_id)])
                    channableApi = conn.apiConnection()
                    tracking_info = {
                        'tracking_code': self.tracking_code,
                        'transporter': self.transporter,
                        'tracking_url': self.tracking_url
                    }
                    shipment_order = channableApi.update_order_shipment(tracking_info, self.sale_id.channable_order_id)
                    logger.info(_("Shipping Order Status................... %s, %s" %(shipment_order, self.sale_id)))
                    channable_order_state = shipment_order.get('status')
                    ## uncomment below code if we want to raise error when order already shipped
                    # if shipment_order.get('status') and shipment_order.get('status') != 'success':
                    #     raise ValidationError(_(shipment_order.get('message')))
                else:
                    raise UserError(_('Please Fill Order Tracking Info Proper'))

            if channable_order_state == 'success' or self.sale_id.is_empty_shipping or self.sale_id.is_fbm_order:
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
                self.sale_id.delivery_validate_error = False
                self.sale_id.is_empty_shipping = False
                return 1
        else:
            return super(StockPicking, self).button_validate()



class ResPartner(models.Model):
    _inherit = 'res.partner'

    courier_name = fields.Char('Courier Name')
    # tracking_url_prefix = fields.Char('URL Prefix')
    house_number = fields.Char('House Number')
    house_number_ext = fields.Char('House Number Ext')
    Address_supplement = fields.Char('Address Supplement')

    def _get_name(self):
        name = super(ResPartner, self)._get_name()
        partner = self
        if self._context.get('show_only_child_name'):
            if partner.company_name or partner.parent_id:
                if not partner.is_company:
                    name = "%s" % (partner.name)
        return name
