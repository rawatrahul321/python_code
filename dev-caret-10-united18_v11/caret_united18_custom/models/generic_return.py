#  -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from datetime import timedelta, datetime

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _default_optype_id(self):
        PickType = self.env['stock.picking.type']
        Picks = PickType.search([('code','=','outgoing')])
        for pick in Picks:
            if pick.sequence_id.company_id.id == self.env.user.company_id.id:
                return pick.id 
        return False

    is_return = fields.Boolean(string="Is Return")
    partner_id = fields.Many2one(
        'res.partner', 'Partner',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True,
        readonly=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},default=_default_optype_id)

    @api.multi
    def _autoconfirm_picking(self):
        if not self._context.get('planned_picking'):
            if not self.env.context.get('return_picking') and self.state == 'draft':
                for picking in self.filtered(lambda picking: picking.state not in ('done', 'cancel') and picking.move_lines):
                    picking.action_confirm()

    @api.multi
    def action_done(self):
        """Changes picking state to done by processing the Stock Moves of the Picking

        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
        # TDE FIXME: remove decorator when migration the remaining
        # TDE FIXME: draft -> automatically done, if waiting ?? CLEAR ME
        todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            # # Explode manually added packages
            # for ops in pick.move_line_ids.filtered(lambda x: not x.move_id and not x.product_id):
            #     for quant in ops.package_id.quant_ids: #Or use get_content for multiple levels
            #         self.move_line_ids.create({'product_id': quant.product_id.id,
            #                                    'package_id': quant.package_id.id,
            #                                    'result_package_id': ops.result_package_id,
            #                                    'lot_id': quant.lot_id.id,
            #                                    'owner_id': quant.owner_id.id,
            #                                    'product_uom_id': quant.product_id.uom_id.id,
            #                                    'product_qty': quant.qty,
            #                                    'qty_done': quant.qty,
            #                                    'location_id': quant.location_id.id, # Could be ops too
            #                                    'location_dest_id': ops.location_dest_id.id,
            #                                    'picking_id': pick.id
            #                                    }) # Might change first element
            # # Link existing moves or add moves when no one is related
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                # Search move with this product
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id) 
                if moves: #could search move that needs it the most (that has some quantities left)
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                                                    'name': _('New Move:') + ops.product_id.display_name,
                                                    'product_id': ops.product_id.id,
                                                    'product_uom_qty': ops.qty_done,
                                                    'product_uom': ops.product_uom_id.id,
                                                    'location_id': pick.location_id.id,
                                                    'location_dest_id': pick.location_dest_id.id,
                                                    'picking_id': pick.id,
                                                   })
                    ops.move_id = new_move.id
                    new_move._action_confirm()
                    todo_moves |= new_move
                    #'qty_done': ops.qty_done})
        todo_moves.sudo()._action_done()
        self.write({'date_done': fields.Datetime.now()})
        return True

    @api.multi
    def button_validate(self):
        self.ensure_one()
        if self.picking_type_id.code == 'outgoing' and self.company_id.parent_id.id:
            warehouse_obj = self.env['stock.warehouse']
            move_line = self.env['stock.move']
            stock = self.env['stock.location']

            StockLocation = stock.sudo().search(['&',('company_id' ,'=', self.partner_id.company_id.id),
                                                 '&',('usage', '=', 'internal'),
                                                   ('return_location','=',False)])
            SourceLocation = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
            picking_type= False
            warehouse_id = warehouse_obj.sudo().search([('company_id', '=', self.partner_id.company_id.id)])
            for warehouse in warehouse_id:
                picking_type = warehouse.in_type_id.id
            for line in self.move_lines:
                available = self.env['stock.quant']._get_available_quantity(line.product_id, line.location_id)
                if available < line.quantity_done:
                    raise UserError(_('You have not enough Available stock of product : ("%s"). Your available stock is "%s"') %
                                    (line.product_id.name, available))
            picking_id = self.sudo().create({'partner_id' : self.env.user.company_id.partner_id.id,
                                             'company_id' : self.partner_id.company_id.id,
                                             'location_id': SourceLocation.id or False,
                                             'location_dest_id' : StockLocation.id or False,
                                             'picking_type_id' : picking_type,
                                             'origin' : self.location_id.complete_name})
            for lines in self.move_lines:
                move_line.sudo().create({'product_id' : lines.product_id.id,
                                         'picking_id' : picking_id.id,
                                         'name' : lines.name,
                                         'priority' : lines.priority,
                                         'company_id' : lines.company_id.parent_id.id,
                                         'product_uom_qty' : lines.quantity_done,
                                         'product_uom' : lines.product_uom.id,
                                         'location_id' : SourceLocation.id or False,
                                         'location_dest_id' : StockLocation.id or False,
                                         'procure_method' : lines.procure_method,
                                         'picking_type_id' : picking_type})
        return super(StockPicking,self).button_validate()

