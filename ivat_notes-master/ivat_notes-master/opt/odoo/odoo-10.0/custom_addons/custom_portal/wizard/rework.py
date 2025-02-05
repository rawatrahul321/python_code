from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime

class StockRework(models.Model):
    _name = 'stock.rework'
    
    @api.multi
    def action_done(self):
        name = ''
        qty_update = 0.0
        workorder_obj = self.env['mrp.workorder'].search([('production_id','=',self.production_id.id),('workcenter_id','=',self.send_workorder_id.workcenter_id.id),('name','=','RE-WORK')])
        print '* W.O. Obj ',workorder_obj
        
        name = self.send_workorder_id.name
        print '*** Selected Re-Order *',name
        curnt_datetime = datetime.datetime.now()
        if self.send_workorder_id.name == name:
            print '* ==Name== *',self.send_workorder_id.workcenter_id.name
            print '====self.send_workorder name',self.send_workorder_id.name
            workcenter_id = self.send_workorder_id.workcenter_id.id
    
        if not workorder_obj:
            print 'Create Rework'
            self.env.cr.execute("insert into mrp_workorder(name,workcenter_id,production_id,create_date,qty_production,state) values (%s,%s,%s,%s,%s,%s)",('RE-WORK',workcenter_id,self.production_id.id,curnt_datetime,1.0,'accept'))
#             self.env.cr.execute("select id from mrp_workorder where name = 'RE-WORK' and production_id=%d"%(self.production_id.id))
        if workorder_obj:
            print '* All WorkOrders For One M.O. *',workorder_obj
            for order in workorder_obj:
                if order.name == 'RE-WORK' and self.send_workorder_id.workcenter_id == order.workcenter_id:
                    print '**Update WorkOrder Qty**',self.send_workorder_id.workcenter_id , order.workcenter_id
                    qty_update = order.qty_production + 1
                    self.env.cr.execute("update mrp_workorder set qty_production=%s where id=%s",(qty_update,order.id,))
        
        # Insert into Info Module
        vals = {
        'name': self.production_id.name,
        'work_order_id': self.workorder_id.id,
        'send_workorder_id': self.send_workorder_id.name,
        'product_id':self.product_id.id,
        'unique_number':self.unique_id.name,
        'date': datetime.datetime.now(),
        'info_date': datetime.datetime.now(),
        'user': self.env.user.id,
        'status': 'Done',
        'rework': True,
        'rework_reason': self.rejection_reason.id,
        }
        res = self.env['info.module'].create(vals)
    
        # Insert into Unique Serial Number
        unique_no_obj = self.env['stock.unique.number'].search([('name','=',self.unique_id.name)])
        print '* Get Unique No. *',unique_no_obj
        list_unique_traceability = []
        for line in self:
            art = {}
            art['name'] = line.production_id.name
            art['work_order'] = line.workorder_id.name
            art['product_id'] = line.product_id.id                
            art['concern_user'] = self.env.user.id
            art['date'] = datetime.datetime.now()
            art['status'] = 'Done'
            art['source_location'] = 15
            art['destination_location'] = line.rework_location_id.id
            art['rework'] = True            
            list_unique_traceability.append((0, 0, art))
        if self.unique_id.name == unique_no_obj.name:
            print '* Posting In Unique Serial No. Module *'
            unique_no_obj.quant_ids = list_unique_traceability    
        return {'type': 'ir.actions.act_window_close'}

    
    @api.onchange('production_id')
    def get_location_id(self):
        self.location_id = self.production_id.location_src_id
    
    rejection_reason = fields.Many2one('reject.reason',string='Rejection Reason')
    workorder_id = fields.Many2one('mrp.workorder', 'Current Work Order')
    production_id = fields.Many2one('mrp.production', 'Manufacturing Order')
    send_workorder_id = fields.Many2one(
        'mrp.workorder', 'Revised Work Order',
        help='Select the Work Order In Which Products has to be reworked.',default=2)
    unique_id = fields.Many2one('stock.unique.number','Serial Number',help='Unique Serial Number')
    product_id = fields.Many2one('product.product', 'Product',required=True)
    rework_qty = fields.Integer('Quantity', default=1, required=True)
    rework_location_id = fields.Many2one('stock.location', 'Re-Work Location')
    location_id = fields.Many2one('stock.location', 'Location', domain="[('usage', '=', 'internal')]")
    
class RejectReason(models.Model):
    _name = 'reject.reason'
    
    name = fields.Char('Reason')
    level = fields.Selection([('low','Low Level'),('mid','Intermediate Level'),
                            ('high','High Level')],string="Select Level")    

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    
    responsible = fields.Many2one('res.users',default=lambda self: self.env.user and self.env.user.id or False)
    qty_production = fields.Float('Original Production Quantity', readonly=True,store=True, related='production_id.product_qty')
    state = fields.Selection([
        ('accept', 'Waiting Acceptance'),
        ('pending', 'Pending'),
        ('ready', 'Ready'),
        ('progress', 'In Progress'),
        ('done', 'Finished'),
        ('cancel', 'Cancelled')], string='Status',
        default='pending')
    
    

    
