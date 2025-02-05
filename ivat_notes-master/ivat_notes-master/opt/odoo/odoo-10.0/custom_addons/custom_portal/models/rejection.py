from odoo import models, fields, api
from odoo.tools.translate import _
import datetime

class StockScrap(models.Model):
    _inherit = 'stock.scrap'
    
    def _get_default_scrap_location_id(self):
        return self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in', [self.env.user.company_id.id, False])], limit=1).id
    
    def _get_default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return None
    
    rejection_reason = fields.Many2one('reject.reason',string='Scrap Reason')
    unique_id = fields.Many2one('stock.unique.number','Serial Number',help='Unique Serial Number')
    production_id = fields.Many2one(
        'mrp.production', 'Manufacturing Order',
        readonly= True)
    workorder_id = fields.Many2one(
        'mrp.workorder', 'Work Order',
        readonly = True,
        help='Not to restrict or prefer quants, but informative.')
    location_id = fields.Many2one(
        'stock.location', 'Location', domain="[('usage', '=', 'internal')]",
        required=True, readonly= True, default=_get_default_location_id)
    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location', default=_get_default_scrap_location_id,
        domain="[('scrap_location', '=', True)]", readonly = True)

        
    @api.multi
    def action_done(self):
            
        # Insert into Info Module
        vals = {
        'name': self.production_id.name,
        'work_order_id': self.workorder_id.id,
        'product_id':self.product_id.id,
        'unique_number':self.unique_id.name,
        'date': datetime.datetime.now(),
        'user': self.env.user.id,
        'status': 'Done',
        'scrap': True,
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
            art['destination_location'] = line.scrap_location_id.id
            art['scrap'] = True            
            list_unique_traceability.append((0, 0, art))
        if self.unique_id.name == unique_no_obj.name:
            print '* Posting In Unique Serial No. Module *'
            unique_no_obj.quant_ids = list_unique_traceability    
        return {'type': 'ir.actions.act_window_close'}
    
    
class RejectReason(models.Model):
    _name = 'reject.reason'
    
    name = fields.Char('Reason')
    level = fields.Selection([('low','Low Level'),('mid','Intermediate Level'),
                            ('high','High Level')],string="Select Level")    

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    
    responsible = fields.Many2one('res.users',default=lambda self: self.env.user and self.env.user.id or False)
    qty_production = fields.Float('Original Production Quantity', readonly=True,store=True, related='production_id.product_qty')

