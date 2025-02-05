from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime

class AutoGenerateUniqueNumber(models.Model):
    _name = 'auto.generate.unique.number'
    
    total_barcode = fields.Integer('No. Of Barcodes To Be Printed')
    message = fields.Char('Message')
    
    @api.multi
    def auto_generate_no(self):
        print '** Entry Unique No. **'
        prefix = ''
        start = 0
        end = 0
        if self.total_barcode == 0:
                    raise UserError(_('No. Of Total Barcode To be Printed Should be Greater Than 0.'))
        now = datetime.datetime.now()
        current_year = now.year
        month_name = now.strftime("%b")
        prefix = ""+ 'AXA' +"" ""+ str(current_year)[2:4] +"" ""+ month_name +"" 
        print '** Prefix **',prefix
        
#         self.env.cr.execute("select max(id) from stock_unique_number")
#         max_id = self.env.cr.fetchall()[0][0]
#         print '** ++MAX ID++ **',max_id
#         self.env.cr.execute("select name from stock_unique_number where id=%s",(max_id,))
        start_no = self.env['stock.unique.number'].search([], limit=1, order='create_date desc')
        print 'Start/Max No***',start_no,   start_no.name        
        
        if not start_no :
            print '** For First Time **'
            start = 1
        if start_no and month_name==start_no.name[5:8]:
            print '** For Current Month Continuity **'
            num = start_no.name.split('/')[1]
            print '** Number After Split **',num
            start = int(num) + 1
        if start_no and month_name !=start_no.name[5:8]:
            print '** For Start Of New Month **'
            print 'Month***',month_name,start_no.name[5:8]
            start = 1
            
        end = start + self.total_barcode                    
        for a in range(start,end):
            print '**Start & End Range Value**',start,end
            print '++** A **++',a
            
            name = ""+ prefix +"" +"/" +"000"+ ""+ str(a) +""
            print 'NAME VALUE+++++',name
            curnt_datetime = datetime.datetime.now()
            user = self.env.user
            qty = 1.0
            self.env.cr.execute("INSERT INTO stock_unique_number(name,create_date,responible_user,product_qty) VALUES (%s,%s,%s,%s)",(name,curnt_datetime,user.id,qty,))
            self.message = 'BARCODE GENERATED SUCCESSFULLY.'
            self.total_barcode = 0
        return {
            "type": "ir.actions.do_nothing",
        }
            
            
            
             
            