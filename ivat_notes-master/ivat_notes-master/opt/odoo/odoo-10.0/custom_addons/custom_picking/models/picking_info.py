from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime


class Picking(models.Model):
    _inherit = "stock.picking"
    
    info_count = fields.Integer(string='Info Count',compute='_compute_info_move_count')
    scan_count = fields.Integer(string='Scan Count',default = 1)
    prod_count = fields.Integer(string='Scan Count',default = 1)
    
    
    @api.multi
    def action_get_packing_info(self):
        self.ensure_one()
        action = self.env.ref('custom_picking.action_packing_info_form').read()[0]
        action['domain'] = [('stock_picking_id', '=', self.id)]
        return action
    
    @api.one
    def truckUpload_verify(self):
        if not self.truck_upload:
            raise UserError(_('Please Scan Barcode.'))
        print 'verify number==',self.truck_upload
        
        pack_code = self.truck_upload.split('~')[2] 
        print 'pack code verify==',pack_code
        prod_obj = self.env['product.product'].search([('default_code','=',pack_code)])
        print 'Prod Obj==',prod_obj,prod_obj.default_code
        info_obj = self.env['packing.info'].search([('product_code','=',pack_code),('stock_picking_id','=',self.id)])          
        print '* Get Packing Info. *',info_obj
        unique_inner_obj = self.env['unique.packing.number'].search([('name','=',self.truck_upload)])
        unique_outer_obj = self.env['unique.outer.packing.number'].search([('name','=',self.truck_upload)])
        
        if self.truck_upload != unique_inner_obj.name and self.truck_upload!= unique_outer_obj.name:
            raise UserError(_('Scanned Serial Number Does Not Exist ! \nPlease Scan Next Barcode.'))
        if not info_obj:
            raise UserError(_('Scanned Serial Number Belongs To Different Picking ! \nPlease Scan Next Barcode.'))
        if info_obj:
            if info_obj.line_ids:
                
                for info in info_obj.line_ids:
                    print 'check box',info.check_verify, info.name
                    if info.name == self.truck_upload and info.check_verify == True:
                        raise UserError(_('Serial Number Already Verified ! \nPlease Scan Next Barcode.'))
                    if info.name == self.truck_upload:
                        info.check_verify = True
            #For Outer Verification
            if info_obj.outer_line_ids:
                for outer_info in info_obj.outer_line_ids:
                    if outer_info.name == self.truck_upload and outer_info.outer_check_verify == True:
                        raise UserError(_('Serial Number Already Verified ! \nPlease Scan Next Barcode.'))
                    if outer_info.name == self.truck_upload:
                        outer_info.outer_check_verify = True
            if not info_obj.outer_line_ids:
                raise UserError(_('Carton Not Even Packed ! \nPlease Scan Next Barcode.'))
        self.truck_upload = ''
        return True
        
    
    @api.one
    def finish_packing(self):
        if not self.pack_box:
            raise UserError(_('Please Scan Barcode.'))
        print 'Pack Number==',self.pack_box
        pack_code = self.pack_box.split('~')[1] 
        print 'pack code 0==',pack_code
        #pack_code1 = pack_code0.split('-')[-1] 
        
        prod_obj = self.env['product.product'].search([('custom_product_code','=',pack_code)])
        print 'Prod Obj==',prod_obj,prod_obj.custom_product_code
        info_obj = self.env['packing.info'].search([('product_code','=',pack_code),('stock_picking_id','=',self.id)])          
        print '* Get Packing Info. *',info_obj
        
        unique_inner_obj = self.env['unique.packing.number'].search([('name','=',self.pack_box)])
        unique_outer_obj = self.env['unique.outer.packing.number'].search([('name','=',self.pack_box)])
        
        if self.pack_box != unique_inner_obj.name and self.pack_box!= unique_outer_obj.name:
            raise UserError(_('Scanned Serial Number Does Not Exist ! \nPlease Scan Next Barcode.'))
        if not info_obj:
            raise UserError(_('Scanned Serial Number Belongs To Different Picking ! \nPlease Scan Next Barcode.'))
        if info_obj:
            # For Inner Carton Barcode
            if info_obj.line_ids:
                if info_obj.line_ids[0].name[0:1] == self.pack_box[0:1]:
                    print 'Inner Info Record Exist====',info_obj.line_ids[-1].name, info_obj.line_ids[-1].name[0:1]
                    if info_obj.line_ids[-1].name == self.pack_box :
                        raise UserError(_("""Serial Number Already Scanned. Can't Scan Same Serial Number! \nPlease Scan Next Barcode."""))

                    list_unique = []
                    for line in self:
                        art = {}
                        art['name'] = line.pack_box
                        art['product_id'] = prod_obj.id
                        art['user'] = self.env.user.id
                        art['date'] = datetime.datetime.now()
                        art['total_qty'] = 1.0
                        art['status'] = 'Done'
                        list_unique.append((0, 0, art))
                    info_obj.line_ids = list_unique
                    info_obj.picked_box += 1 
                    if info_obj.box == info_obj.picked_box:
                        print 'change state to finish.'
                        info_obj.write({'state':'finished'})
            #For Outer Carton Barcode
            print 'outer check------',info_obj.outer_line_ids,  self.pack_box
            if info_obj.outer_line_ids:
                if info_obj.outer_line_ids[0].name[0:1] == self.pack_box[0:1]:
                    print 'Outer Info Record Exist====',info_obj.outer_line_ids                    
                    if info_obj.outer_line_ids[-1].name == self.pack_box :
                        raise UserError(_("""Serial Number Already Scanned. Can't Scan Same Serial Number! \nPlease Scan Next Barcode."""))
                    
                    list_unique = []
                    for line in self:
                        art = {}
                        art['name'] = line.pack_box
                        art['product_id'] = prod_obj.id           
                        art['user'] = self.env.user.id
                        art['date'] = datetime.datetime.now()
                        art['total_qty'] = 1.0
                        art['status'] = 'Done'
                        list_unique.append((0, 0, art))
                    info_obj.outer_line_ids = list_unique
                    info_obj.picked_box_outer += 1 
            
            
            
            #If inner carton barcode record does'nt exist
            if not info_obj.line_ids:
                if self.pack_box[0:1] == 'I':
                    print 'No Existing Inner Info Record'
                    list_unique_traceability = []
                    for line in self:
                        art = {}
                        art['name'] = line.pack_box
                        art['product_id'] = prod_obj.id           
                        art['user'] = self.env.user.id
                        art['date'] = datetime.datetime.now()
                        art['total_qty'] = 1.0
                        art['status'] = 'Done'
                        list_unique_traceability.append((0, 0, art))
                    info_obj.line_ids = list_unique_traceability
                    info_obj.picked_box += 1 
                    info_obj.write({'state':'progress'})
            #If Outer carton Barcode record does not exist.
            if not info_obj.outer_line_ids:
                if self.pack_box[0:1] == 'O':                
                    print 'No Existing Outer Info Record'
                    list_unique_traceability = []
                    for line in self:
                        art = {}
                        art['name'] = line.pack_box
                        art['product_id'] = prod_obj.id           
                        art['user'] = self.env.user.id
                        art['date'] = datetime.datetime.now()
                        art['total_qty'] = 1.0
                        art['status'] = 'Done'
                        list_unique_traceability.append((0, 0, art))
                    info_obj.outer_line_ids = list_unique_traceability
                    info_obj.picked_box_outer += 1 
                    info_obj.write({'state':'progress'})
                
            if info_obj.box == info_obj.picked_box and info_obj.outer_box == info_obj.picked_box_outer:
                print 'Picking For Product Completed'
                info_obj.status = 'Completed'
                info_obj.write({'state':'finished'})
                
            #Posting In Unique Inner Module
            list_inner_traceability = []
            for line in self:
                art = {}
                art['name'] = line.name
                art['product_id'] = prod_obj.id           
                art['concern_user'] = self.env.user.id
                art['date'] = datetime.datetime.now()
                art['total_qty'] = 1.0
                art['status'] = 'Done'
                list_inner_traceability.append((0, 0, art))
            if self.pack_box == unique_inner_obj.name:
                print '* Posting In Inner Unique Serial No. Module *'
                unique_inner_obj.use_unused_barcode = True
                unique_inner_obj.line_ids = list_inner_traceability
            #Posting In Unique Outer Module
            list_outer_traceability = []
            for line in self:
                art = {}
                art['name'] = line.name
                art['product_id'] = prod_obj.id           
                art['concern_user'] = self.env.user.id
                art['date'] = datetime.datetime.now()
                art['total_qty'] = 1.0
                art['status'] = 'Done'
                list_outer_traceability.append((0, 0, art))
            if self.pack_box == unique_outer_obj.name:
                print '* Posting In Outer Unique Serial No. Module *'
                unique_outer_obj.use_unused_barcode = True
                unique_outer_obj.line_ids = list_outer_traceability
                
        self.pack_box = ''   
        return True
    
    @api.multi
    def _compute_info_move_count(self):
        data = self.env['packing.info'].read_group([('stock_picking_id', 'in', self.ids)], ['stock_picking_id'], ['stock_picking_id'])
        count_data = dict((item['stock_picking_id'][0], item['stock_picking_id_count']) for item in data)
        for packorder in self:
            packorder.info_count = count_data.get(packorder.id, 0)
    
class PackingInfo(models.Model):
    _name = 'packing.info'
    _description = 'Packing Info'
    
    name = fields.Char('Unique Number')
    product_id = fields.Many2one('product.product', 'Product Code & Name')
    product_code = fields.Char('Product Code')
    total_qty = fields.Float("PC's")
    box = fields.Float('Inner Box')
    outer_box = fields.Float('Outer Box')
    picked_box = fields.Float('Picked Inner Box')
    picked_box_outer = fields.Float('Picked Outer Box')    
    
    user = fields.Many2one('res.users','Responsible User')
    date = fields.Datetime('Date & Time')
    status = fields.Char('Status')
    info_date = fields.Date('Date',help='Info Date')
    stock_picking_id = fields.Many2one('stock.picking','Picking')
     
    warehouse_quantity = fields.Char(string='Quantity Per Warehouse')
    state = fields.Selection([
            ('draft', 'Pending'),
            ('progress', 'In progress'),
            ('finished', 'Done'),
            ],default='draft')
    line_ids = fields.One2many('packing.details','pack_id','Packing Details')
    outer_line_ids = fields.One2many('outer.packing.details','pack_id','Outer Packing Details')
    
class PackingDetails(models.Model):
    _name = 'packing.details'
    
    pack_id = fields.Many2one('packing.info')
    name = fields.Char('Unique Number')
    product_id = fields.Many2one('product.product', 'Product Code & Name')
    total_qty = fields.Float("PC's")
    
    user = fields.Many2one('res.users','Responsible User')
    date = fields.Datetime('Date & Time')
    status = fields.Char('Status')
    check_verify = fields.Boolean('Verify Scan',default = False)
    
class OuterPackingDetails(models.Model):
    _name = 'outer.packing.details'
    
    pack_id = fields.Many2one('packing.info')
    name = fields.Char('Unique Number')
    product_id = fields.Many2one('product.product', 'Product Code & Name')
    total_qty = fields.Float("PC's")
    
    user = fields.Many2one('res.users','Responsible User')
    date = fields.Datetime('Date & Time')
    status = fields.Char('Status')
    outer_check_verify = fields.Boolean('Verify Outer Scan',default = False)
    
    
    
    
    
    
