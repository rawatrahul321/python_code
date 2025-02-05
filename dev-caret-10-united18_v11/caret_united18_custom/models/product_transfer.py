#  -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from datetime import timedelta, datetime

class ProductTransfer(models.Model):
    _name = "product.transfer"

    name = fields.Char(string="Name",required=True, states={'open': [('readonly', False)]})
    state = fields.Selection([('open', 'New'), ('confirm', 'Validated')], string='Status', required=True, readonly=True, copy=False, default='open')
    transfer_date = fields.Date(string="Transfer Date")
    transfer_line_ids = fields.One2many('product.transfer.line','transfer_id',string = 'Product Transfer')
    company_id = fields.Many2one('res.company', string='company', default=lambda self: self.env.user.company_id.id)

    @api.multi
    def validate_product_transfer(self):
        """ Transfer or move quantity one product to another. """

        StockMove = self.env['stock.move.line']
        StockQuant = self.env['stock.quant']
        Stock = self.env['stock.move']
        Scrapped = self.env.ref('stock.stock_location_scrapped')

        for transfer in self.transfer_line_ids:
            SourceQuant = StockQuant.search([('product_id','=',transfer.source_product_id.id),('location_id','=',transfer.source_location_id.id)])
            DestinationQuant = StockQuant.search([('product_id','=',transfer.final_product_id.id),('location_id','=',transfer.destination_location_id.id)])
            if SourceQuant:
                SourceQuant.quantity = SourceQuant.quantity - transfer.qty_transfer
            if DestinationQuant:
                DestinationQuant.quantity = DestinationQuant.quantity + transfer.qty_transfer
            else :
                StockQuant.create({'product_id':transfer.final_product_id.id,
                                   'location_id':transfer.destination_location_id.id,
                                   'quantity': transfer.qty_transfer})

            source_move = StockMove.create({'product_id' : transfer.source_product_id.id,
                                        'product_uom_id': transfer.source_product_id.uom_id.id,
                                        'qty_done' : transfer.qty_transfer,
                                        'location_id' : transfer.source_location_id.id,
                                        'location_dest_id' : Scrapped.id,
                                        })
            stock_move_one = Stock.create({
                                        'name': transfer.source_product_id.name + ' to ' + transfer.final_product_id.name,
                                        'product_id' : transfer.source_product_id.id,
                                        'product_uom': transfer.source_product_id.uom_id.id,
                                        'product_uom_qty' : transfer.qty_transfer,
                                        'ordered_qty': transfer.qty_transfer,
                                        'location_id' : transfer.source_location_id.id,
                                        'location_dest_id' : transfer.destination_location_id.id,
                                        })
            stock_move_second = Stock.create({
                                        'name': transfer.final_product_id.name + ' to ' + transfer.source_product_id.name,
                                        'product_id' : transfer.final_product_id.id,
                                        'product_uom': transfer.final_product_id.uom_id.id,
                                        'product_uom_qty' : transfer.qty_transfer,
                                        'ordered_qty': transfer.qty_transfer,
                                        'location_id' : transfer.destination_location_id.id,
                                        'location_dest_id' : transfer.source_location_id.id,
                                        })
            destination_move = StockMove.create({'product_id' : transfer.final_product_id.id,
                                        'product_uom_id': transfer.final_product_id.uom_id.id,
                                        'qty_done' : transfer.qty_transfer,
                                        'location_id' : transfer.source_location_id.id,
                                        'location_dest_id' : transfer.destination_location_id.id,
                                        })

            source_move.write({'reference': transfer.source_product_id.name + ' to ' + transfer.final_product_id.name})
            destination_move.write({'reference': transfer.source_product_id.name + ' to ' + transfer.final_product_id.name})
            source_move.state = 'done'
            destination_move.state = 'done'
            stock_move_one.state = 'done'
            stock_move_second.state = 'done'
        self.state = 'confirm'
        return True

class ProductTransferLine(models.Model):
    _name = "product.transfer.line"

    @api.onchange('source_product_id','source_location_id')
    def _onchange_available_qty(self):
        StockQuantObj = self.env['stock.quant']
        if self.source_location_id:
            quantity = 0
            stockquant_Qty = StockQuantObj.search([('location_id','=',self.source_location_id.id),('product_id','=',self.source_product_id.id)])
            for quant in stockquant_Qty:
                quantity = quantity + quant.quantity
            self.available_qty = quantity

    @api.onchange('qty_transfer')
    def _onchange_qty_transfer(self):
        if self.available_qty < self.qty_transfer:
            raise UserError(_('You can not add Transfer Quantity more than Available Quantity'))

    @api.onchange('final_product_id','source_product_id')
    def _onchange_final_product(self):
        if self.final_product_id and self.source_product_id and (self.final_product_id.id == self.source_product_id.id):
            raise UserError(_('Please Create or Select Different Product than Source Product'))

    source_product_id = fields.Many2one('product.product',string="Source Product",required=True)
    source_location_id = fields.Many2one('stock.location',string="Source Location",required=True)
    available_qty = fields.Float(string='Available Qty')
    final_product_id = fields.Many2one('product.product',string="Final Product",required=True)
    destination_location_id = fields.Many2one('stock.location',string="Destination Location",required=True)
    qty_transfer = fields.Float('Qty Transfer')
    transfer_id = fields.Many2one('product.transfer')

class StockLocation(models.Model):
    _inherit = "stock.location"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=None):
        context = self._context or {}
        locations = []
        ProductObj = self.env['product.product']
        if context.get('transfer_product_id'):
            product_browse = ProductObj.browse(context.get('transfer_product_id'))
         
            if len(product_browse.stock_quant_ids) > 0:
             
                for quant in product_browse.stock_quant_ids:
                    if quant.location_id and quant.location_id.usage == 'internal' and quant.location_id.company_id.id == self.env.user.company_id.id:
                        locations.append(quant.location_id.id)
            args += [('id', 'in', locations)]
        if context.get('destination_product_id'):
            stock_location = self.env['stock.location'].search(['&',('usage','=','internal'),
                                                                ('return_location','=',False)])
            for location in stock_location:
                if location.company_id.id == self.env.user.company_id.id:
                    locations.append(location.id)

            args += [('id', 'in', locations)]
        return super(StockLocation, self).name_search(name, args, operator=operator, limit=limit)


