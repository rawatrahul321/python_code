from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime

class AutoGeneratePackingNumber(models.Model):
    _name = 'auto.generate.packing.number'
    
    def _default_product_name(self):
        workorder_id = self.env['mrp.workorder'].browse(self._context.get('active_id'))
        print 'WorkOrder Id: - ',   workorder_id
        product_id = self.env['product.product'].search([('id','=',workorder_id.product_id.id)])
        return product_id and product_id.id or False
    
    def _default_product_qty(self):
        print 'Entry Product Qty'
        workorder_id = self.env['mrp.workorder'].browse(self._context.get('active_id'))
        print 'WorkOrder Id: - ',   workorder_id
        product_qty = workorder_id.qty_production
        print 'Product Qty',product_qty
        return product_qty or False
    
    def _default_innerCartonItems(self):
        workorder_id = self.env['mrp.workorder'].browse(self._context.get('active_id'))
        product_id = self.env['product.product'].search([('id','=',workorder_id.product_id.id)])
        return product_id.inner_carton_qty
    
    total_barcode = fields.Integer('No. Of Barcodes To Be Printed')
    product_id = fields.Many2one('product.product', string='Product', default=lambda self: self._default_product_name())   
    product_qty = fields.Float('Quantity', default=lambda self: self._default_product_qty())
    message = fields.Char('Message')
    items_in_inner_carton = fields.Float("Items In Inner Carton", default=lambda self: self._default_innerCartonItems())
    
    
    @api.multi
    def auto_generate_no(self):
        print '** Entry Unique Packing No. **'
        prefix = ''
        start = 0
        end = 0
        if self.product_qty == 0:
                    raise UserError(_('No. Of Total Barcode To be Printed Should be Greater Than 0.'))
        now = datetime.datetime.now()
        current_year = now.year
        month_name = now.strftime("%b")
        print 'Current Month ==',month_name
        print 'PRD ID@@@@@@@',self.product_id.id
        prd_temp_id  = self.env['product.template'].search([('id','=',self.product_id.product_tmpl_id.id)])
        print "Prd Tmpl COde===",prd_temp_id,   prd_temp_id.custom_product_code
        prefix = ""+ 'I~' +"" "" + ""+ prd_temp_id.custom_product_code +""+ "" '~' ""+ ""+ str(current_year)[2:4] +"" ""+ month_name +"" + "" '/' ""
        print '** Prefix **',prefix
        
        start_no = self.env['unique.packing.number'].search([], limit=1, order='create_date desc')
        print 'Start/Max No***',start_no, start_no.name
        
        if not start_no :
            print '** For First Time **'
            start = 1
        if start_no and month_name==str(start_no.name.split('19')[1][0:3]) :
            print '** For Current Month Continuity **'
            num0 = start_no.name.split('/')[1]
            num = num0.split('~')[0]
            print '** Number After Split **',num
            start = int(num) + 1
        if start_no and month_name !=str(start_no.name.split('19')[1][0:3]) :
            print '** For Start Of New Month **'
            print 'Current Month',month_name #start_no.name[12:15]
            start = 1
        
        total_barcode = round(self.product_qty / self.items_in_inner_carton)
        print 'Total Barcode==',total_barcode
        end = start + int(total_barcode)            
        for a in range(start,end):
            print '**Start & End Range Value**',start,end
            print '++** A **++',a
            
            name = ""+ prefix +"" +"00"+ ""+ str(a) +"" + ""+ "" '~' ""+str(int(self.product_id.inner_carton_qty)) +""
            print 'NAME VALUE+++++',name
            curnt_datetime = datetime.datetime.now()
            user = self.env.user
            qty = 1.0
            self.env.cr.execute("INSERT INTO unique_packing_number(name,create_date,responible_user,product_qty) VALUES (%s,%s,%s,%s)",(name,curnt_datetime,user.id,qty,))
            self.message = "" + str(int(total_barcode)) +""+ ' INNER CARTON BARCODE GENERATED SUCCESSFULLY.'
            self.total_barcode = 0
        return {
            "type": "ir.actions.do_nothing",
        }
            
            
            
             
            