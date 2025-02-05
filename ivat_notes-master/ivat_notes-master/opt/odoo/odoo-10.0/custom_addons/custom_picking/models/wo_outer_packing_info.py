from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
import math

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    
    outer_info_count = fields.Integer(string='Outer Info Count',compute='_compute_outer_info_move_count')
    final_outer_id = fields.Char('Outer Packaging Barcode')
    outer_box = fields.Float("Outer Box",compute='get_Total_InnerBoxes')
    outer_picked_box = fields.Float("Outer Picked Box",default=0)
    
    @api.multi
    def action_get_workOrder_outer_packing_info(self):
        self.ensure_one()
        action = self.env.ref('custom_picking.action_outer_work_order_packing_info_form').read()[0]
        action['domain'] = [('work_order_id', '=', self.id)]
        return action
    
    @api.one
    def get_Total_OuterBoxes(self):
        b = ((1.0 / (self.product_id.inner_carton * self.product_id.inner_carton_qty)) * self.qty_production)
        self.outer_box = math.ceil(b)     
            
    @api.one
    def finish_outer_packing_no(self):
        self.get_Total_OuterBoxes()
        if not self.final_outer_id:
            raise UserError(_('Please Scan Barcode.'))
        print 'Outer Barcode Number==',self.final_outer_id

        outer_pack_obj = self.env['work.order.outer.packing.info'].search([('name','=',self.final_outer_id) , ('work_order_id','=',self.id)])
        print 'Outer Obj==',outer_pack_obj
        if self.final_outer_id == outer_pack_obj.name:
            raise UserError(_('Current Unique Serial Number Already Scanned ! \n\nPlease Scan Next Product.'))
        
        unique_no_obj = self.env['unique.outer.packing.number'].search([('name','=',self.final_outer_id)])
        print '* Get Unique No. *',unique_no_obj
        if self.final_outer_id != unique_no_obj.name:
            raise UserError(_('Scanned Serial Number Does Not Exist ! \nPlease Scan Next Product.'))

        
        #new
        if unique_no_obj:
            for a in unique_no_obj.line_ids:
                if a.product_id.default_code != self.product_id.default_code:
                    print '* Product Code Validation *',a.product_id.default_code,      self.product_id.default_code
                    raise UserError(_('Current Unique Serial Number Belong TO Different Product ! \n\nPlease Scan Next Product.'))
        
        infoObj = self.env['work.order.outer.packing.info'].search([('work_order_id','=',self.id)])
        print '++ InfoObj ++',infoObj  
        if infoObj:
            print 'Info Record Exist===='
            
            outer_pick_box = self.outer_picked_box + 1
            print 'outer_pick_box==',outer_pick_box,self.outer_picked_box
            vals = {
                'name': self.final_outer_id,
                'work_order_id':self.id,
                'product_id':self.product_id.id,
                'product_code':self.product_id.default_code,
                'date': datetime.datetime.now(),
                'info_date': datetime.datetime.now(),
                'user': self.env.user.id,
                'status': 'Done',
                'total_qty': self.qty_production,
                'outer_box': self.outer_box,
                'outer_picked_box': outer_pick_box
            }
            self.env['work.order.outer.packing.info'].create(vals)
            self.outer_picked_box += 1
            #check if scanning completed.
            infoObj1 = self.env['work.order.outer.packing.info'].search([('work_order_id','=',self.id)])[-1]
            if infoObj1.outer_box == infoObj1.outer_picked_box:
                p_qty = self.production_id.product_qty
                production_move = self.production_id.move_finished_ids.filtered(lambda x: (x.product_id.id == self.production_id.product_id.id) and (x.state not in ('done', 'cancel')))
                production_move.quantity_done = p_qty
                print 'P.Move===',production_move,  p_qty
                production_consume = self.production_id.move_raw_ids            
                print '* Production Consume *',production_consume
                for a in production_consume:
                    print a
                    a.quantity_done = p_qty
                    print 'a++++++',a.quantity_done
    #                 a.quantity_done = self.qty_production
                
                self.button_finish()
                self.final_outer_id = ''
                return True
                #raise UserError(_("""Scanning Completed! \nPlease Scan Next Product."""))
            
        if not infoObj:
            print 'No Existing Inner Info Record'
            vals = {
                'name': self.final_outer_id,
                'work_order_id':self.id,
                'product_id':self.product_id.id,
                'product_code':self.product_id.default_code,
                'date': datetime.datetime.now(),
                'info_date': datetime.datetime.now(),
                'user': self.env.user.id,
                'status': 'Done',
                'total_qty': self.qty_production,
                'outer_box': self.outer_box,
                'outer_picked_box': 1
            }
            self.env['work.order.outer.packing.info'].create(vals)
            self.outer_picked_box += 1        
        
        #Update entry in unique module
        list_unique_traceability = []
        for line in self:
            art = {}
            art['name'] = line.production_id.name
            art['total_qty'] = line.qty_production
            art['product_id'] = line.product_id.id                
            art['concern_user'] = self.env.user.id
            art['date'] = datetime.datetime.now()
            art['status'] = 'Done'
            list_unique_traceability.append((0, 0, art))
            
        if self.final_outer_id == unique_no_obj.name:
            print '* Posting In Unique Serial No. Module *'
            unique_no_obj.use_unused_barcode = True
            unique_no_obj.line_ids = list_unique_traceability
        
        # Update workorder quantity produced
        if self.qty_produced <= self.qty_production:
            if self.product_id.group_product == True:
                
#                 uniqueObj = self.env['stock.unique.number'].search([('name','=',self.final_unique_id)])
#                 infoObj = self.env['info.module'].search([('unique_number','=',self.final_unique_id),('work_order_id','=',self.id),('rework','=',False)])          
#                 print '++ Get Info No. ++',infoObj
#                 for line in uniqueObj.quant_ids:
#                     productAttr = line.product_id.prod_attribute
                    
                
                total_comp = self.product_id.no_of_component
                print '+ Entry if Group Product +',total_comp,  self.scan_count
                if total_comp * self.prod_count == self.scan_count:
                    print 'COunt True'
                    self.qty_produced += 1
                    self.prod_count += 1
            else:    
                print '* Else Entry *'
                self.qty_produced += 1
        if self.qty_produced == self.qty_production:
            p_qty = self.production_id.product_qty
            production_move = self.production_id.move_finished_ids.filtered(lambda x: (x.product_id.id == self.production_id.product_id.id) and (x.state not in ('done', 'cancel')))            
            print '* Production Move FG *',self.qty_production,  production_move.quantity_done,  production_move
            production_move.quantity_done = p_qty
#             production_move.quantity_done = production_move.quantity_done
           
            production_consume = self.production_id.move_raw_ids            
            print '* Production Consume *',production_consume
            for a in production_consume:
                a.quantity_done = p_qty
#                 a.quantity_done = self.qty_production
            
            self.button_finish()
        self.scan_count += 1
        self.final_outer_id = ''
                
        return True
    
    @api.multi
    def _compute_outer_info_move_count(self):
        data = self.env['work.order.outer.packing.info'].read_group([('work_order_id', 'in', self.ids)], ['work_order_id'], ['work_order_id'])
        count_data = dict((item['work_order_id'][0], item['work_order_id_count']) for item in data)
        for packorder in self:
            packorder.outer_info_count = count_data.get(packorder.id, 0)
    
class WorkOrderOuterPackingInfo(models.Model):
    _name = 'work.order.outer.packing.info'
    _description = 'Outer Packing Info'
    
    work_order_id = fields.Many2one('mrp.workorder','Work Order')
    name = fields.Char('Unique Number')
    product_id = fields.Many2one('product.product', 'Product Name')
    product_code = fields.Char('Product Code')
    total_qty = fields.Float("PC's")
    outer_box = fields.Float('Outer Box')
    outer_picked_box = fields.Float('Packed Outer Box')
    
    user = fields.Many2one('res.users','Responsible User')
    date = fields.Datetime('Date & Time')
    status = fields.Char('Status')
    info_date = fields.Date('Date',help='Info Date')
     
    #warehouse_quantity = fields.Char(string='Quantity Per Warehouse')
#     state = fields.Selection([
#             ('draft', 'Pending'),
#             ('progress', 'In progress'),
#             ('finished', 'Done'),
#             ],default='draft')
    

    
    
    
    
    
    