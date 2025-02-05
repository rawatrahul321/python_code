from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
import math

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    
    info_count = fields.Integer(string='Info Count',compute='_compute_info_move_count')
    final_inner_id = fields.Char('Inner Packaging Barcode')
    box = fields.Float("Inner Box",compute='get_Total_InnerBoxes')
    picked_box = fields.Float("Picked Box",default=0)
    
    @api.multi
    def action_get_work_order_packing_info(self):
        self.ensure_one()
        action = self.env.ref('custom_picking.action_work_order_packing_info_form').read()[0]
        action['domain'] = [('work_order_id', '=', self.id)]
        return action
    
    @api.one
    def get_Total_InnerBoxes(self):
        a = ((1.0 / self.product_id.inner_carton_qty) * self.qty_production)
        self.box = math.ceil(a)

    @api.one
    def finish_inner_packing_no(self):
        self.get_Total_InnerBoxes()
        if not self.final_inner_id:
            raise UserError(_('Please Scan Barcode.'))
        print 'Inner Barcode Number==',self.final_inner_id

        inner_pack_obj = self.env['work.order.packing.info'].search([('name','=',self.final_inner_id) , ('work_order_id','=',self.id)])
        print 'Inner Obj==',inner_pack_obj
        if self.final_inner_id == inner_pack_obj.name:
            raise UserError(_('Current Unique Serial Number Already Scanned ! \n\nPlease Scan Next Product.'))

        unique_no_obj = self.env['unique.packing.number'].search([('name','=',self.final_inner_id)])
        print '* Get Unique No. *',unique_no_obj
        if self.final_inner_id != unique_no_obj.name:
            raise UserError(_('Scanned Serial Number Does Not Exist ! \nPlease Scan Next Product.'))


        #new
        if unique_no_obj:
            prd_temp_id  = self.env['product.template'].search([('id','=',self.product_id.id)])
            if  str(unique_no_obj.name.split('~')[1]) != str(prd_temp_id.custom_product_code):
                raise UserError(_('Current Unique Serial Number Belong TO Different Product ! \n\nPlease Scan Next Product.'))
        infoObj = self.env['work.order.packing.info'].search([('work_order_id','=',self.id)])
        print '++ InfoObj ++',len(infoObj) ,infoObj
        if len(infoObj) >= 1:
            print 'Info Record Exist===='

            infoObj1 = self.env['work.order.packing.info'].search([('work_order_id','=',self.id)])[-1]
            if infoObj1.box == infoObj1.picked_box:
                self.final_inner_id = ''
                raise UserError(_("""Scanning Completed! \nPlease Scan Next Product."""))
            if infoObj1.name == self.final_inner_id:
                raise UserError(_("""Serial Number Already Scanned. Can't Scan Continuous Same Barcode! \nPlease Scan Next Product."""))
            pick_box = self.picked_box + 1
            print 'pick_box==',pick_box,self.picked_box
            vals = {
                'name': self.final_inner_id,
                'work_order_id':self.id,
                'product_id':self.product_id.id,
                'product_code':self.product_id.default_code,
                'date': datetime.datetime.now(),
                'info_date': datetime.datetime.now(),
                'user': self.env.user.id,
                'status': 'Done',
                'total_qty': self.qty_production,
                'box': self.box,
                'picked_box': pick_box
            }
            self.env['work.order.packing.info'].create(vals)
            self.picked_box += 1

        if not infoObj:
            print 'No Existing Inner Info Record'
            vals = {
                'name': self.final_inner_id,
                'work_order_id':self.id,
                'product_id':self.product_id.id,
                'product_code':self.product_id.default_code,
                'date': datetime.datetime.now(),
                'info_date': datetime.datetime.now(),
                'user': self.env.user.id,
                'status': 'Done',
                'total_qty': self.qty_production,
                'box': self.box,
                'picked_box': 1
            }
            self.env['work.order.packing.info'].create(vals)
            self.picked_box += 1        
        
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
            
        if self.final_inner_id == unique_no_obj.name:
            print '* Posting In Unique Serial No. Module *'
            unique_no_obj.use_unused_barcode = True
            unique_no_obj.line_ids = list_unique_traceability
        
        # Update workorder quantity produced
        if self.production_id.product_id.outer_packing_wo == True:
            infoObj1 = self.env['work.order.packing.info'].search([('work_order_id','=',self.id)])[-1]
            if infoObj1.box == infoObj1.picked_box:
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
                    self.button_finish()
                    self.final_inner_id = ''
                    return True

        self.final_inner_id = ''
        return True

    @api.multi
    def _compute_info_move_count(self):
        data = self.env['work.order.packing.info'].read_group([('work_order_id', 'in', self.ids)], ['work_order_id'], ['work_order_id'])
        count_data = dict((item['work_order_id'][0], item['work_order_id_count']) for item in data)
        for packorder in self:
            packorder.info_count = count_data.get(packorder.id, 0)

class WorkOrderPackingInfo(models.Model):
    _name = 'work.order.packing.info'
    _description = 'Packing Info'

    work_order_id = fields.Many2one('mrp.workorder','Work Order')
    name = fields.Char('Unique Number')
    product_id = fields.Many2one('product.product', 'Product Name')
    product_code = fields.Char('Product Code')
    total_qty = fields.Float("PC's")
    box = fields.Float('Inner Box')
    picked_box = fields.Float('Packed Inner Box')

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


class ProductProduct(models.Model):
    _inherit = "product.template"

    outer_packing_wo = fields.Boolean('No Outer Packing',
                      help ='Check this if outer packing work order not required',default=False)

    custom_product_code = fields.Char('Product Code',help="Numeric Product Code For Carton Barcode Purpose")
