# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_utils


class StockMultiTransfer(models.Model):
    _name = "stock.multi.transfer"
    _description = "Stock Multi Location Transfer"
    _order = "id desc"

    @api.model
    def _default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].\
            search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        else:
            raise UserError(_(
                'You must define a warehouse for the company: %s.') % (company_user.name,))

    name = fields.Char(
        string="Name", required=True,
        states={'open': [('readonly', False)]})
    state = fields.Selection([
        ('open', 'New'),
        ('confirm', 'Validated')],
        string='Status', required=True, readonly=True, copy=False, default='open')
    transfer_date = fields.Date(string="Transfer Date", default=fields.Date.today())
    # transfer_line_ids = fields.One2many('product.transfer.line','transfer_id',string = 'Product Transfer')
    company_id = fields.Many2one(
        'res.company', string='company',
        default=lambda self: self.env.user.company_id.id)
    src_location_id = fields.Many2one(
        'stock.location', 'Source Location',
        readonly=True, required=True,
        states={'open': [('readonly', False)]},
        default=_default_location_id)
    line_ids = fields.One2many(
        'stock.multi.transfer.line', 'transfer_id', string='Lines',
        copy=True, readonly=False,
        states={'confirm': [('readonly', True)]})
    move_ids = fields.One2many(
        'stock.move', 'transfer_id', string='Created Moves',
        states={'confirm': [('readonly', True)]})
    lot_id = fields.Many2one(
        'stock.production.lot', 'Inventoried Lot/Serial Number',
        copy=False, readonly=True,
        states={'draft': [('readonly', False)]},
        help="Specify Lot/Serial Number to focus your inventory on a particular Lot/Serial Number.")

    def action_done(self):
        self.action_check()
        self.write({'state': 'confirm'})
        self.post_inventory()
        return True

    def post_inventory(self):
        # The inventory is posted as a single step which means quants cannot be moved from an internal location to another using an inventory
        # as they will be moved to inventory loss, and other quants will be created to the encoded quant location. This is a normal behavior
        # as quants cannot be reuse from inventory location (users can still manually move the products before/after the inventory if they want).
        self.mapped('move_ids').filtered(lambda move: move.state != 'done')._action_done()

    def action_check(self):
            self.mapped('move_ids').unlink()
            self.line_ids._generate_moves()


class StockMultiTransferLine(models.Model):
    _name = "stock.multi.transfer.line"
    _description = "Stock Multi Location Transfer Line"
    _order = "id desc"

    transfer_id = fields.Many2one(
        'stock.multi.transfer', 'Transfer',
        index=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('type', '=', 'product')],
        index=True, required=True)
    product_qty = fields.Float(
        'Quantity',
        digits=dp.get_precision('Product Unit of Measure'), default=0)
    dest_location_id = fields.Many2one(
        'stock.location', 'Location',
        index=True, required=True)
    prod_lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id','=',product_id)]")
    company_id = fields.Many2one(
        'res.company', 'Company', related='transfer_id.company_id',
        index=True, readonly=True, store=True)
    # TDE FIXME: necessary ? -> replace by location_id
    state = fields.Selection(
        'Status',  related='transfer_id.state', readonly=True)

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        self.ensure_one()
        return {
            'name': _('Stock Transfer:') + (self.product_id.display_name or ''),
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': qty,
            'date': self.transfer_id.transfer_date or False,
            'company_id': self.transfer_id.company_id.id,
            'transfer_id': self.transfer_id.id,
            'state': 'confirmed',
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'lot_id': self.prod_lot_id.id,
                'product_uom_qty': 0,  # bypass reservation here
                'product_uom_id': self.product_id.uom_id.id,
                'qty_done': qty,
                'package_id': False,
                'result_package_id': False,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
            })]
        }

    def _generate_moves(self):
        moves = self.env['stock.move']
        for line in self:
            vals = line._get_move_values(
                self.product_qty, self.transfer_id.src_location_id.id, line.dest_location_id.id, False)
            moves |= self.env['stock.move'].create(vals)
        return moves


class StockMoveInh(models.Model):
    _inherit = "stock.move"

    transfer_id = fields.Many2one(
        'stock.multi.transfer', 'Transfer',
        index=True, ondelete='cascade')

