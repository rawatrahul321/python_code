from odoo import api, fields, models, _
from odoo.tools.translate import _
from odoo import api, fields, models, tools, SUPERUSER_ID, _
import datetime
from odoo.exceptions import UserError

class ProductCartonLabel(models.TransientModel):
    _name = 'product.carton.label'
    
    name = fields.Char('Message')
    no_of_labels = fields.Integer("Number Of Label Copies",default=1)
    product_id = fields.Many2one('product.template',string="Product")
    carton_type = fields.Selection([
       ('inner', 'Inner Carton'),
       ('outer', 'Outer Carton')],string='Select Carton Label', default='inner')
    carton_qty = fields.Integer('Carton Quantity')
    
    @api.multi  
    def print_report(self):
        context = self._context 
        print 'active_model====',context.get('active_model')
        if context.get('active_model') == 'product.template':
            obj = self.env['product.template'].search([('id', '=', context.get('active_id'))]) 
            self.product_id = obj.id       
            
            if self.product_id:
                if self.carton_type == 'inner':
                    self.name = 'Inner Labels Generated Successfully' 
                    return self.env['report'].get_action(self, 'custom_portal.inner_carton')  
                if self.carton_type == 'outer':
                    self.name = 'Outer Labels Generated Successfully' 
                    self.carton_qty = obj.inner_carton * obj.inner_carton_qty
                    return self.env['report'].get_action(self, 'custom_portal.outer_carton')  
            else:
                raise UserError((_("Please set barcode for the product %s") % obj.product_id.name))
            
        if context.get('active_model') == 'mrp.production':
            current_id = context.get('active_id')
            mrpObj = self.env['mrp.production'].search([('id','=',current_id)])
            prod_id = self.env['product.product'].search([('id','=',mrpObj.product_id.id)])
            obj = self.env['product.template'].search([('id', '=', prod_id.product_tmpl_id.id)]) 
            print 'obj=====',obj
            self.product_id = obj.id     
            
            if self.product_id:
                if self.carton_type == 'inner':
                    self.name = 'Inner Labels Generated Successfully' 
                    return self.env['report'].get_action(self, 'custom_portal.inner_carton')  
                if self.carton_type == 'outer':
                    self.name = 'Outer Labels Generated Successfully' 
                    self.carton_qty = obj.inner_carton * obj.inner_carton_qty
                    return self.env['report'].get_action(self, 'custom_portal.outer_carton')  
            else:
                raise UserError((_("Please set barcode for the product %s") % obj.product_id.name))




    
    



     
     
     
                  
        