from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
import datetime
import math

class Picking(models.Model):
    _inherit = "stock.picking"

    picking_operation_product_ids = fields.One2many(
        'stock.picking.operation', 'picking_id', 'Non pack',
        domain=[('product_id', '!=', False)],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    pack_box = fields.Char('Unique Packing Number')
    truck_upload = fields.Char('Truck Upload Verification')
    check_transfer = fields.Boolean('Check Transfer',default = False)

    @api.multi
    def transfer_picking(self):
        list_transfer = []
        for line in self.move_lines:

            art = {}
            art['name'] = line.product_id.default_code
            art['product_id'] = line.product_id.id
            art['partner_id'] = line.partner_id.id
            art['picking_id'] = self.id
            art['ordered_qty'] = line.product_uom_qty
            art['status'] = 'Pending'

            list_transfer.append((0, 0, art))
        self.picking_operation_product_ids = list_transfer

        pick_opns = self.env['stock.picking.operation'].search([('picking_id','=',self.id)])
        for pick in pick_opns:
            print'Create Picking View'
            prd_temp_id  = self.env['product.template'].search([('id','=',pick.product_id.id)])
            vals = {
                'product_id': pick.product_id.id,
                'product_code': prd_temp_id.custom_product_code,
                'warehouse_quantity':pick.warehouse_quantity,
                'total_qty': pick.ordered_qty,
                'box': pick.box,
                'outer_box': pick.outer_box,
                'picked_box':pick.picked_box,
                'stock_picking_id':self.id,
                'status': 'In-Process',
                'user': self.env.user.id,
                'date': datetime.datetime.now(),
                'info_date': datetime.datetime.now(),
                }
            self.env['packing.info'].create(vals)
            self.check_transfer = True

class StockPickingOperations(models.Model):
    _name = 'stock.picking.operation'
    _description = "Stock Picking"

    warehouse_quantity = fields.Char(compute='get_warehouse_quantity', string='Quantity Per Warehouse')

    @api.one
    def get_box(self):
        print 'Ordered Qty==',self.ordered_qty, self.product_id.inner_carton,  self.product_id.outer_carton
        a = ((1.0 / self.product_id.inner_carton_qty) * self.ordered_qty)
        print 'Inner Box',a,    math.ceil(a)
        self.box = math.ceil(a)

        total_outer_qty = self.product_id.inner_carton * self.product_id.inner_carton_qty
        b = ((1.0 / total_outer_qty) * self.ordered_qty)
        print 'B--',b
        self.outer_box = math.ceil(b)
        print 'Outer Carton Qty',self.outer_box

    def get_warehouse_quantity(self):

        for record in self:
            print '# TMPL id #',record.product_id.product_tmpl_id
            warehouse_quantity_text = ''
            product_id = self.env['product.product'].sudo().search([('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)])
            if product_id:
                quant_ids = self.env['stock.quant'].sudo().search([('product_id','=',product_id[0].id),('location_id.usage','=','internal')])
                t_warehouses = {}
                for quant in quant_ids:
                    if quant.location_id:
                        if quant.location_id not in t_warehouses:
                            t_warehouses.update({quant.location_id:0})
                        t_warehouses[quant.location_id] += quant.qty

                tt_warehouses = {}

                print 't_warehouses========',t_warehouses
                for location in t_warehouses:
                    warehouse = False
                    location1 = location
                    print '++ location ++',location,   location.complete_name
                    while (not warehouse and location1):
                        warehouse_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',location1.id)])
                        if len(warehouse_id) > 0:
                            warehouse = True
                        else:
                            warehouse = False
                        location1 = location1.location_id
                    if warehouse_id:
                        print 'tt_warehouses=====',tt_warehouses
                        if warehouse_id.name not in tt_warehouses:
                            tt_warehouses.update({warehouse_id.name:0})
                        tt_warehouses[warehouse_id.name] += t_warehouses[location]

                for item in t_warehouses:
                    if t_warehouses[item] != 0:
                        warehouse_quantity_text = warehouse_quantity_text + ' ** ' + item.complete_name + ': ' + str(t_warehouses[item])

#                 for item in tt_warehouses:
#                     if tt_warehouses[item] != 0:
#                         import pdb;pdb.set_trace()
#                         warehouse_quantity_text = warehouse_quantity_text + ' ** ' + item + ': ' + str(tt_warehouses[item])
                record.warehouse_quantity = warehouse_quantity_text
                self.get_box()

    name = fields.Char('Product Code')
    product_id = fields.Many2one('product.product', 'Product Code & Name',domain=[('type', 'in', ['product', 'consu'])], index=True, required=True)  
    partner_id = fields.Many2one('res.partner','Partner')
    picking_id = fields.Many2one('stock.picking','Picking')

    ordered_qty = fields.Float("PC's", default=0.0, digits=dp.get_precision('Product Unit of Measure'), required=True)
    to_do = fields.Float("To-Do")
    status = fields.Char("Status")
    box = fields.Float("Inner Box",compute='get_box')
    outer_box = fields.Float('Outer Box',compute='get_box')
    picked_box = fields.Float("Picked Box")
    
class StockMove(models.Model):
    _inherit = "stock.move"
    
#     @api.model
#     def create(self, vals):
#         #print 'vals===',vals
#         # TDE CLEANME: why doing this tracking on picking here ? seems weird
#         perform_tracking = not self.env.context.get('mail_notrack') and vals.get('picking_id')
#         if perform_tracking:
#             picking = self.env['stock.picking'].browse(vals['picking_id'])
#             initial_values = {picking.id: {'state': picking.state}}
#         vals['ordered_qty'] = vals.get('product_uom_qty')
#         res = super(StockMove, self).create(vals)
#         print "vals['name']====",vals.get('name')[0:4],type(vals.get('name')[0:4]),str(vals.get('name')[0:4])
#         if str(vals.get('name')[0:4]) == 'INV:':
#             print 'Dont Create Custom Picking=='
#         if not str(vals.get('name')[0:4]) == 'INV:':
#             print 'Custom Picking Created=='
#             self.env['stock.picking.operation'].create(vals)
#         if perform_tracking:
#             picking.message_track(picking.fields_get(['state']), initial_values)
#         return res
#     
#     @api.multi
#     def assign_picking(self):
#         print '--Assign Picking Entry--'
#         """ Try to assign the moves to an existing picking that has not been
#         reserved yet and has the same procurement group, locations and picking
#         type (moves should already have them identical). Otherwise, create a new
#         picking to assign them to. """
#         Picking = self.env['stock.picking']
#         for move in self:
#             print 'move-------',move
#             recompute = False
#             picking = Picking.search([
#                 ('group_id', '=', move.group_id.id),
#                 ('location_id', '=', move.location_id.id),
#                 ('location_dest_id', '=', move.location_dest_id.id),
#                 ('picking_type_id', '=', move.picking_type_id.id),
#                 ('printed', '=', False),
#                 ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
#             if not picking:
#                 recompute = True
#                 picking = Picking.create(move._get_new_picking_values())
#             move.write({'picking_id': picking.id})
#             pack_update = self.env['stock.picking.operation'].search([('picking_id','=',False)])
#             for pack in pack_update:
#                 print 'pack---------',pack
#                 pack.write({'picking_id': picking.id})
# 
#             if recompute:
#                 move.recompute()
#         return True

