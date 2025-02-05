from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import datetime



class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    final_unique_id = fields.Char('Current Unique Number')
    #info_count = fields.Integer(string='Info Count',compute='_get_info_module_count')
    info_record_count = fields.Integer(string='Info Count',compute='_get_info_module_count')
    info_record_count1 = fields.Integer(string='Info Count',compute='_get_info_module_count1')
    scan_count = fields.Integer(string='Scan Count',default = 1)
    prod_count = fields.Integer(string='Scan Count',default = 1)

    @api.one
    def _get_info_module_count(self):
        print '=+ INFO COUNT  +='
        record_count = self.env['info.module'].search_count([('work_order_id','=',self.id)])
        print '** Info Record Count **',record_count
        self.info_record_count = record_count
    @api.one
    def _get_info_module_count1(self):
        print '=+ INFO COUNT  +='
        record_count = self.env['info.module'].search_count([('work_order_id','=',self.id)])
        print '** Info Record Count **',record_count
        self.info_record_count1 = record_count

    @api.multi
    def action_get_info_record(self):
        self.ensure_one()
        action = self.env.ref('info_module.action_info_module_form').read()[0]
        action['domain'] = [('work_order_id', '=', self.id)]
        return action


    @api.model
    def finish_serial_no(self):

        p_qty = 0.0
        infoCount = 0
        info_obj = self.env['info.module'].search([('unique_number','=',self.final_unique_id),('work_order_id','=',self.id),('rework','=',False)])
        print '* Get Info No. *',info_obj
        if self.info_record_count >= self.qty_production:
            print("dsaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",self.info_record_count)
            print("EWQQQQQQQQQQQQQQQQQQQQQQQQQQQQ",self.qty_production)
            raise UserError("Quantity produced is greater then Quantity production/Please contact Administartor for further details")

        if self.final_unique_id == info_obj.unique_number:
            raise UserError(_('Current Unique Serial Number Already Scanned ! \n\nPlease Scan Next Product.'))

        unique_no_obj = self.env['stock.unique.number'].search([('name','=',self.final_unique_id)])
        print '* Get Unique No. *',unique_no_obj
        if self.final_unique_id != unique_no_obj.name:
            raise UserError(_('Scanned Serial Number Does Not Exist ! \nPlease Scan Next Product.'))
        if unique_no_obj:
            for a in unique_no_obj.quant_ids:
                if a.product_id.product_validation != self.product_id.product_validation:
                    print '* Product Code Validation *',a.product_id.product_validation,      self.product_id.product_validation
                    raise UserError(_('Current Unique Serial Number Belong TO Different Product ! \n\nPlease Scan Next Product.'))

        #If Group Product
        if self.product_id.group_product == True:
            uniqueObj = self.env['stock.unique.number'].search([('name','=',self.final_unique_id)])
            infoCount = self.env['info.module'].search([('work_order_id','=',self.id),('rework','=',False)])
            print 'Info Count===',infoCount
            if not uniqueObj.quant_ids:
                    raise UserError(_('Unused Serial Number ! \n\nPlease Scan Next Product.'))
            #if len(uniqueObj.quant_ids) > 1:
            #    print 'Length uniqueObj.quant_ids',len(uniqueObj.quant_ids)
            #    raise UserError(_('Unique Barcode For Product Attribute Should be Used Once.'))
            if infoCount:
                print 'Info Record Exist===='
                infoObj = self.env['info.module'].search([('work_order_id','=',self.id),('rework','=',False)])[-1]
                print 'InfoObj===',infoObj,  infoObj.product_id.prod_attribute
                print 'Unique Obj COunt Product Id ', uniqueObj.quant_ids[-1].product_id.prod_attribute
                if uniqueObj.quant_ids[-1].product_id.prod_attribute == infoObj.product_id.prod_attribute:
                    raise UserError(_("""Serial Number Product Attribute Already Scanned. Can't Scan Continuous Same Attribute! \nPlease Scan Next Product."""))

                for line in uniqueObj.quant_ids:
                        productName = line.product_id.id
                vals = {
                    'name': self.production_id.name,
                    'work_order_id':self.id,
                    'product_id': productName,
                    'unique_number':self.final_unique_id,
                    'date': datetime.datetime.now(),
                    'info_date': datetime.datetime.now(),
                    'user': self.env.user.id,
                    'status': 'Done',
                }
                res = self.env['info.module'].create(vals)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%vals%%%%%%%%%%%%%%%%%%%%%%%%%%%",vals)
            if not infoCount:
                print 'No Existing Info Record'
                vals = {
                    'name': self.production_id.name,
                    'work_order_id':self.id,
                    'product_id':self.product_id.id,
                    'unique_number':self.final_unique_id,
                    'date': datetime.datetime.now(),
                    'info_date': datetime.datetime.now(),
                    'user': self.env.user.id,
                    'status': 'Done',
                }
                res = self.env['info.module'].create(vals)
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%vals2%%%%%%%%%%%%%%%%%%%%%%%%%%%",vals)

        else:
            date = datetime.datetime.now()
            date1 = self.env.user.id
             # self.env.cr.execute("select id from sale_order where crn_no='"+cirn_no+"'")
             # txn_id=self.env.cr.fetchall()[0]
            # print(insert into info_module(name, work_order_id, product_id,unique_number,date,info_date,user,status) values("+str(self.production_id.name)+","+str(self.id)+","+str(self.product_id.id)+","+str(self.final_unique_id)+","+str(date)+","+str(date1)+","+str(Done)+")")
            self.env.cr.execute("insert into info_module(name, work_order_id, product_id , unique_number, date, info_date, status) values('"+str(self.production_id.name)+"','"+str(self._origin.id)+"','"+str(self.product_id.id)+"','"+str(self.final_unique_id)+"','"+str(datetime.datetime.now())+"','"+str(datetime.datetime.now())+"','"+str('Done')+"')")

             # print(txn_id)
             # print("update payment_detail set deposit_date='"+str(self.next_chq_date1)+"',cheque_status_acc='received' where txn_id="+str(txn_id[0])+" and cheque_number='"+str(self.cheque_number)+"'")
             # self.env.cr.execute("update payment_detail set deposit_date='"+str(self.next_chq_date1)+"',cheque_status_acc='not_received' where txn_id="+str(txn_id[0])+" and cheque_number='"+str(self.cheque_number)+"'")
            # vals = {
            #     'name': self.production_id.name,
            #     'work_order_id':self._origin.id,
            #     'product_id':self.product_id.id,
            #     'unique_number':self.final_unique_id,
            #     'date': datetime.datetime.now(),
            #     'info_date': datetime.datetime.now(),
            #     'user': self.env.user.id,
            #     'status': 'Done',
            # }
            # res = self.env['info.module'].create(vals)
            # print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%vals3%%%%%%%%%%%%%%%%%%%%%%%%%%%",vals)


        list_unique_traceability = []
        for line in self:
            art = {}
            art['name'] = line.production_id.name
            art['work_order'] = line.name
            art['product_id'] = line.product_id.id
            art['concern_user'] = self.env.user.id
            art['date'] = datetime.datetime.now()
            art['status'] = 'Done'
            art['source_location'] = 15
            art['destination_location'] = 7
            list_unique_traceability.append((0, 0, art))

        if self.final_unique_id == unique_no_obj.name:
            print '* Posting In Unique Serial No. Module *'
            unique_no_obj.use_unused_barcode = True
            unique_no_obj.quant_ids = list_unique_traceability



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
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%qty_produced",self.qty_produced)
            else:
                print '* Else Entry *'
                self.qty_produced += 1
                # self.create({'qty_produced':self.qty_produced})
                # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2",self.create({'qty_produced':self.qty_produced}))
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%self.else.qty_produced",self.qty_produced)
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
        self.final_unique_id = ''
        print("I am here")
        return True


    #@api.multi
    #def _compute_info_move_count(self):
    #    data = self.env['info.module'].read_group([('work_order_id', 'in', self.ids)], ['work_order_id'], ['work_order_id'])
    #    count_data = dict((item['work_order_id'][0], item['work_order_id_count']) for item in data)
    #    for workorder in self:
    #        workorder.info_count = count_data.get(workorder.id, 0)

class InfoModule(models.Model):
    _name = 'info.module'
    _description = 'Info Module'

    name = fields.Char('Manufacturing Order')
    work_order_id = fields.Many2one('mrp.workorder','Work Order')
    unique_number = fields.Char('Unique Number')
    product_id = fields.Many2one('product.product', 'Product')
    user = fields.Many2one('res.users','Responsible User')
    date = fields.Datetime('Date & Time')
    status = fields.Char('Status')
    send_workorder_id = fields.Char('Revised Work Order',help='For Re-Work Purpose.')
    rework = fields.Boolean('Re-Work')
    rework_reason = fields.Many2one('reject.reason',string='Re - Work Reason')
    scrap = fields.Boolean('Scrap')
    info_date = fields.Datetime('Date',help='Info Date')

class ProductProduct(models.Model):
    _inherit = "product.template"

    product_validation = fields.Char('Product Validation Code',help='Enter Only Numeric Product Code For Validation.')
