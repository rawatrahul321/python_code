# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re
import ipdb

class Account(models.Model):
    _inherit = 'account.journal'

class AccountPayment(models.Model):
    _inherit = 'account.payment.method'

class IrSequence(models.Model):
    _inherit = 'ir.sequence.date_range'

class Company(models.Model):
    _inherit = 'res.company'


    def send_sms_to_company_partner(self, **kwargs):
        print("self==================",self)
        # ipdb.set_trace()
        partner = kwargs['partner']
        sms_template = self.env['ir.model.data'].get_object('caret_sms', 'company_creation_sms_template')
        ctx = dict(self._context)
        ctx.update({
                'partner' : partner.name,
                'mlogin' : kwargs['mlogin'],
                'mpswrd' : kwargs['mpswrd'],
                'ulogin' : kwargs['ulogin'],
                'upswrd' : kwargs['upswrd']
            })
        sms_rendered_content = self.env['sms.body.template'].\
            with_context(ctx).\
            render_template(
                sms_template.template_body, sms_template.model, self.id)
        # sms_rendered_content = """
        #     Dear %s ,
        #     login deatils for:
        #     manager:
        #         login = %s
        #         password = %s
        #     user:
        #         login = %s
        #         password = %s
        # """ %(partner.name,
        #       kwargs['mlogin'],
        #       kwargs['mpswrd'],
        #       kwargs['ulogin'],
        #       kwargs['upswrd'])
        api_key = self.env['ir.config_parameter'].sudo().get_param('caret_sms.textlocal_api_key')
        sender = self.env['ir.config_parameter'].sudo().get_param('caret_sms.sender')
        to_number = ''
        to_mobile = partner.mobile
        if to_mobile:
            if len(to_mobile) == 10:
                to_number = str(91) + to_mobile
            elif '+' in to_mobile and len(to_mobile) == 13:
                to_number = to_mobile.replace('+','').strip()
            elif '+' in to_mobile and len(to_mobile) == 11:
                to_number = to_mobile.replace('+','').strip()
            elif '+' in to_mobile and len(to_mobile) == 11:
                to_number = to_mobile.replace('+','').strip()
            else:
                to_number = self.partner_id.mobile
            SMS_record = self.env['sms.sms'].create({'textlocal_api_key':api_key,
                                        'to_number': to_number,
                                        'message': sms_rendered_content,
                                        'sender': sender,
                                        'res_id': self.id or False,
                                        'res_model': 'res.company',
                                        })
            SMS_record.with_context(ctx).sendSMS()

    @api.multi
    def set_sequence(self, partner_id):
        sequence = ''
        if partner_id:
            sequence = self.env['ir.sequence'].next_by_code('customer.id')
            partner_id.sudo().customer_id = sequence

    @api.model
    def create(self,vals):
        res = super(Company,self).create(vals)
        if res.partner_id:
            self.set_sequence(res.partner_id)
        # if vals.get('mobile'):
        #     res.partner_id = vals['mobile']
        Default_Grp = []
        res_users = self.env['res.users']
        ResPartner = self.env['res.partner']
        location = self.env['stock.location']
        UserObj = self.env['res.users']
        ChartTemplateObj = self.env['account.chart.template']
        PropertyObj = self.env['ir.property']
        AccountObj = self.env['account.account']
        AccountJrnlObj = self.env['account.journal']
        PosConfigObj = self.env['pos.config']
        StockPickingTypeObj = self.env['stock.picking.type']
        StockWarehouseeObj = self.env['stock.warehouse']
        IrSequenceObj = self.env['ir.sequence']
        GrpObj = self.env['res.groups']
        AccountTax = self.env['account.tax']
        FiscalPosition = self.env['account.fiscal.position']
        FiscalPositionTax = self.env['account.fiscal.position.tax']
        #load chart of account
        #AdminUser = UserObj.browse(1)
        united18_grp = GrpObj.sudo().search([('name','=ilike','United18')])
        if united18_grp:
            if self.env.uid in [x.id for x in united18_grp.users]:
                AdminUser = res_users.sudo().browse(self.env.uid)
                ChartTempId = AdminUser.company_id.chart_template_id.id
                ChartTemplateRecord = ChartTemplateObj.sudo().search([('id','=',ChartTempId)])
                if not ChartTemplateRecord:
                    raise UserError(_('First Set Chart Of Template For %s user.')%AdminUser.name)
                else:
                    ChartTemplateRecord = ChartTemplateRecord[0]

                DefaultChart = ChartTemplateRecord
                wizard = self.env['wizard.multi.charts.accounts'].sudo().create({
                    'company_id': res.id,
                    'chart_template_id': DefaultChart.id,
                    'code_digits': DefaultChart.code_digits,
                    'transfer_account_id': DefaultChart.transfer_account_id.id,
                    'currency_id': DefaultChart.currency_id.id,
                    'bank_account_code_prefix': DefaultChart.bank_account_code_prefix,
                    'cash_account_code_prefix': DefaultChart.cash_account_code_prefix,
                })
                wizard.sudo().onchange_chart_template_id()
                wizard.sudo().execute()
        
                #customer location for new company
                c_location = self.env.ref('stock.stock_location_locations_partner', raise_if_not_found=False)
                customer_location = location.sudo().create({
                    'name': 'Customers',
                    'usage': 'customer',
                    'location_id': c_location and c_location.id or False,
                    'company_id' : res.id,
                })
                #vendors location for new company
                v_location = self.env.ref('stock.stock_location_locations_partner', raise_if_not_found=False)
                vendor_location = location.sudo().create({
                    'name': 'Vendors',
                    'usage': 'supplier',
                    'location_id': v_location and v_location.id or False,
                    'company_id' : res.id,
                })
                
                u18_cust_location = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
                u18_vendor_location = self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False)
                res.partner_id.property_stock_customer=u18_cust_location.id
                res.partner_id.property_stock_supplier=u18_vendor_location.id
        
                # Return Location
                
                parent_location = location.sudo().search([('usage','=','view'),('company_id','=',False)],limit=1)
                return_location_stock = location.sudo().create({
                    'usage': 'internal',
                    'name': 'Stock Return',
                    'location_id': parent_location and parent_location.id or False,
                    'company_id' : res.id,
                    'return_location':True,
                })
                parent_location_vendor = location.sudo().search([('usage','=','view'),('company_id','=',False)],limit=1)
                return_location_vendor = location.sudo().create({
                    'usage': 'supplier',
                    'name': 'Return to Vendor',
                    'location_id': parent_location_vendor and parent_location_vendor.id or False,
                    'company_id' : res.id,
                    'return_location':True,
                })

                # Search Groups for Default access
                inventory_user_grp = self.env.ref('stock.group_stock_user')
                Default_Grp.append(inventory_user_grp.id)
                account_user_grp = self.env.ref('account.group_account_invoice')
                Default_Grp.append(account_user_grp.id)
                purchase_user_grp = self.env.ref('purchase.group_purchase_user')
                Default_Grp.append(purchase_user_grp.id)
                pos_user_grp = self.env.ref('point_of_sale.group_pos_user')
                Default_Grp.append(pos_user_grp.id)
                emp_user_grp = self.env.ref('base.group_user')
                Default_Grp.append(emp_user_grp.id)

                #create two user (one is manager and 2nd is normal user) for each company
                AdminRecevableProperty = AdminUser.partner_id.property_account_receivable_id

                AdminPayableProperty = AdminUser.partner_id.property_account_payable_id

                res.sudo().partner_id.property_account_receivable_id = AdminRecevableProperty.id
                res.sudo().partner_id.property_account_payable_id = AdminPayableProperty.id
                res.sudo().partner_id.company_id = AdminUser.company_id.id
                res.sudo().partner_id.customer = True
                # res.sudo().partner_id.mobile = res.phone
                res.sudo().street = vals.get('street')
                res.sudo().street2 = vals.get('street2')
                res.sudo().city = vals.get('city')
                res.sudo().state_id = vals.get('state_id')
                res.sudo().zip = vals.get('zip')
                res.sudo().country_id = vals.get('country_id')

                ManagerReceive = AccountObj.sudo().search([('name','=',AdminUser.partner_id.property_account_receivable_id.name),
                                                 ('code','=',AdminUser.partner_id.property_account_receivable_id.code),('company_id','=',res.id)])

                ManangerPay = AccountObj.sudo().search([('name','=',AdminUser.partner_id.property_account_payable_id.name),
                                                 ('code','=',AdminUser.partner_id.property_account_payable_id.code),('company_id','=',res.id)])
                
                partner_manager = ResPartner.sudo().create({
                                                     'name': vals['name'] + ' Manager',
                                                     'company_type': 'person',
                                                     'customer':False,
                                                     'property_account_receivable_id':ManagerReceive.id,
                                                     'property_account_payable_id':ManangerPay.id,
                                                     'property_stock_customer':customer_location.id,
                                                     'property_stock_supplier':vendor_location.id,
                                                     'email':(vals['name'].strip().lower() + 'manager').replace(' ',''),
                                                     'company_id': res.id,
                                                     })
                mlogin = (vals['name'].lower() + 'manager').replace(' ','')
                manager=res_users.sudo().create({
                        'name': vals['name'] + ' Manager',
                        'login': mlogin,
                        'company_ids': [(4,res.id)],
                        'company_id': res.id,
                        'groups_id': Default_Grp,
                        'partner_id':partner_manager and partner_manager.id or False,
                })
                managerPswrd = vals['name'] + 'Manager'
                manager.password = managerPswrd

#                 manager.partner_id.property_account_receivable_id = ManagerReceive.id
#                 manager.partner_id.property_account_payable_id = ManangerPay.id
#                 manager.partner_id.property_stock_customer=customer_location.id
#                 manager.partner_id.property_stock_supplier=vendor_location.id
                partner_user = ResPartner.sudo().create({
                                                 'name': vals['name'] + ' User',
                                                 'company_type': 'person',
                                                 'customer':False,
                                                 'property_account_receivable_id':ManagerReceive.id,
                                                 'property_account_payable_id':ManangerPay.id,
                                                 'property_stock_customer':customer_location.id,
                                                 'property_stock_supplier':vendor_location.id,
                                                 'email':(vals['name'].strip().lower() + 'user').replace(' ',''),
                                                 'company_id': res.id,
                                                     })
                uLogin = (vals['name'].strip().lower() + 'user').replace(' ','')
                user=res_users.sudo().create({
                        'name': vals['name'] + ' User',
                        'login': uLogin,
                        'company_ids': [(4,res.id)],
                        'company_id': res.id,
                        'groups_id': Default_Grp,
                        'partner_id':partner_user and partner_user.id or False,
                })
                userPwsrd = vals['name'] + 'User'
                user.password = userPwsrd
                
#                 user.partner_id.property_account_receivable_id = ManagerReceive.id
#                 user.partner_id.property_account_payable_id = ManangerPay.id
#                 user.partner_id.property_stock_customer=customer_location.id
#                 user.partner_id.property_stock_supplier=vendor_location.id
            
                AdminUser.company_ids += res
                res.parent_id = AdminUser.company_id.id
                res.send_sms_to_company_partner(
                        mlogin = mlogin,
                        mpswrd = managerPswrd,
                        ulogin = uLogin,
                        upswrd = userPwsrd,
                        partner = res.partner_id
                    )
                # Create POS Sales Operation Type
                
                Warehouse_id = StockWarehouseeObj.sudo().search([('company_id','=',res.id)],limit=1)
                DefSrcLocation_id = location.sudo().search([('company_id','=',res.id),('name','=ilike','Stock')],limit=1)
                DefDestLocation_id = location.sudo().search([('company_id','=',res.id),('name','=ilike','Customer')],limit=1)
                PosSeq = IrSequenceObj.sudo().create({'name':'Picking POS',
                                      'prefix':'POS',
                                      'padding': 5,
                                      'company_id': res.id,
                                      })
                POSOpType = StockPickingTypeObj.sudo().create({'name': 'PoS Orders',
                                                        'sequence_id': PosSeq and PosSeq.id or False,
                                                        'default_location_src_id': DefSrcLocation_id and DefSrcLocation_id.id or False,
                                                        'default_location_dest_id': DefDestLocation_id and DefDestLocation_id.id or False,
                                                        'warehouse_id': Warehouse_id and Warehouse_id.id or False,
                                                        'code': 'outgoing',
                                            })
                
                # Warehouse,Picking Operation, Sequence
        
                Warehouse_ids = StockWarehouseeObj.sudo().search([('company_id','=',res.id)])
                if Warehouse_ids:
                    for wh in Warehouse_ids:
                        picking_type = StockPickingTypeObj.sudo().search([('warehouse_id','=',wh.id)])
                        for pt in picking_type:
                            pt.sequence_id.company_id = res.id
                
                # POS Payment Method FOr Company
                PayMethods = []
                DigitalPay = AccountJrnlObj.sudo().create({'name':'Digital',
                                                    'journal_user': True,
                                                    'type': 'bank',
                                                    'code': 'DIGI',
                                                    'company_id': res.id,
                                                    })

                PayMethods.append(DigitalPay.id)
                CashPay = AccountJrnlObj.sudo().search([('name','=ilike','Cash'),('type','=','cash'),('company_id','=',res.id)],limit=1)

                if CashPay:
                    CashPay.journal_user = True
                else:
                    CashPay = AccountJrnlObj.sudo().create({'name':'Cash',
                                                        'journal_user': True,
                                                        'type': 'cash',
                                                        'code': 'CSH',
                                                        'company_id': res.id,
                                                        })

                SaleJrnlPOS = AccountJrnlObj.sudo().create({'name':'POS Sale Journal',
                                                    'type': 'sale',
                                                    'code': 'salep',
                                                    'company_id': res.id,
                                                    })

                StockLocation = self.env['stock.warehouse'].sudo().search([('company_id', '=', res.id)], limit=1).lot_stock_id
                
                PayMethods.append(CashPay.id)
                #POS Config Record for Session Start
                InvJrnl = AccountJrnlObj.sudo().search([('type', '=', 'sale'), ('company_id', '=', res.id)], limit=1)
                PosConfigObj.sudo().create({'name': str(res.name) + ' ' + 'POS',
                                     'company_id': res and res.id or False,
                                     'journal_ids': [(6, 0, PayMethods)],
                                     'journal_id': SaleJrnlPOS and SaleJrnlPOS.id or False, 
                                     'invoice_journal_id': InvJrnl and InvJrnl.id or False,
                                     'stock_location_id':StockLocation and StockLocation.id or False,
                                     'picking_type_id': POSOpType and POSOpType.id or False,
                                     'module_pos_discount': True,
                                     'discount_product_id': self.env.ref('point_of_sale.product_product_consumable').id or False,
                                     })

        # 0% tax create and update fiscal position
        # search accounts for add in new created taxes
        sgst_purchase_account = AccountObj.search([('name','=','SGST Receivable'),
                                                   ('company_id','=',res.id)])
        sgst_sale_account = AccountObj.search([('name','=','SGST Payable'),
                                              ('company_id','=',res.id)])
        cgst_purchase_account = AccountObj.search([('name','=','CGST Receivable'),
                                                   ('company_id','=',res.id)])
        cgst_sale_account = AccountObj.search([('name','=','CGST Payable'),
                                               ('company_id','=',res.id)])
        purchase_exp = AccountObj.search([('name','=','Purchase Expense'),
                                          ('company_id','=',res.id)])
        sale_exp = AccountObj.search([('name','=','Local Sales'),
                                      ('company_id','=',res.id)])
        igst_purchase_account = AccountObj.search([('name','=','IGST Receivable'),
                                                   ('company_id','=',res.id)])
        igst_sale_account = AccountObj.search([('name','=','IGST Payable'),
                                               ('company_id','=',res.id)])

        fiscal_position_id = FiscalPosition.search([('name','=','Inner State GST'),
                                                    ('company_id','=',res.id)])
        outer_position_id = FiscalPosition.search([('name','=','Outer State GST'),
                                                   ('company_id','=',res.id)])

        # create taxes for 0%
        sgst_purchase_id = AccountTax.create({'type_tax_use' : 'purchase',
                           'name' : 'SGST Purchase 0%',
                           'company_id' : res.id,
                           'description' : 'SGST 0%',
                           'account_id' : sgst_purchase_account.id or False,
                           'refund_account_id' : purchase_exp.id or False,
                           'tag_ids': [(6, 0, [7])] or False,
                           'amount' : 0.0,
                           'tax_group_id' : 2 or False,
                           })
        cgst_purchase_id = AccountTax.create({'type_tax_use' : 'purchase',
                           'name' : 'CGST Purchase 0%',
                           'company_id' : res.id,
                           'description' : 'CGST 0%',
                           'account_id' : cgst_purchase_account.id or False,
                           'refund_account_id' : purchase_exp.id or False,
                           'tag_ids': [(6, 0, [8])] or False,
                           'amount' : 0.0,
                           'tax_group_id' : 3 or False,
                           })
        sgst_sale_id = AccountTax.create({'type_tax_use' : 'sale',
                           'name' : 'SGST Sale 0%',
                           'company_id' : res.id,
                           'description' : 'SGST 0%',
                           'account_id' : sgst_sale_account.id or False,
                           'refund_account_id' : sale_exp.id or False,
                           'tag_ids': [(6, 0, [7])] or False,
                           'amount' : 0.0,
                           'tax_group_id' : 2 or False,
                           })
        cgst_sale_id = AccountTax.create({'type_tax_use' : 'sale',
                           'name' : 'CGST Sale 0%',
                           'company_id' : res.id,
                           'description' : 'CGST 0%',
                           'account_id' : cgst_sale_account.id or False,
                           'refund_account_id' : sale_exp.id or False,
                           'tag_ids': [(6, 0, [8])] or False,
                           'amount' : 0.0,
                           'tax_group_id' : 3 or False,
                           })
        igst_purchase_id = AccountTax.create({'type_tax_use' : 'purchase',
                           'name' : ' IGST 0%',
                           'company_id' : res.id,
                           'description' : 'IGST 0%',
                           'account_id' : igst_purchase_account.id or False,
                           'refund_account_id' : purchase_exp.id or False,
                           'tag_ids': [(6, 0, [9])] or False,
                           'amount' : 0.0,
                           'tax_group_id' : 4 or False,
                           })
        igst_sale_id = AccountTax.create({'type_tax_use' : 'sale',
                           'name' : ' IGST 0%',
                           'company_id' : res.id,
                           'description' : 'IGST 0%',
                           'account_id' : igst_sale_account.id or False,
                           'refund_account_id' : sale_exp.id or False,
                           'tag_ids': [(6, 0, [9])] or False,
                           'amount' : 0.0,
                           'tax_group_id' : 4 or False,
                           })
        gst_purchase_id = AccountTax.create({'type_tax_use' : 'purchase',
                           'name' : ' GST Purchase 0%',
                           'company_id' : res.id,
                           'description' : 'GST 0%',
                           'amount' : 0.0,
                           'amount_type' : 'group',
                           'children_tax_ids' : [(6, 0, [sgst_purchase_id.id,cgst_purchase_id.id])],
                           })
        gst_sale_id = AccountTax.create({'type_tax_use' : 'sale',
                           'name' : ' GST Sale 0%',
                           'company_id' : res.id,
                           'description' : 'GST 0%',
                           'amount' : 0.0,
                           'amount_type' : 'group',
                           'children_tax_ids' : [(6, 0, [sgst_sale_id.id,cgst_sale_id.id])],
                           })

#         update fiscal position 
        for tax_id in fiscal_position_id.tax_ids:
            percent_check = re.findall("\d+", tax_id.tax_src_id.name)
            value = int(percent_check[0])/2
            if '.0' in str(value):
                value=int(value)
            if tax_id.tax_src_id.type_tax_use == 'sale':
                sgst_name = 'SGST Sale '+str(value)+'%'
                cgst_name = 'CGST Sale '+str(value)+'%'
            else:
                sgst_name = 'SGST Purchase '+str(value)+'%'
                cgst_name = 'CGST Purchase '+str(value)+'%'
            sgst_tax_id = AccountTax.search(['&',('name','=',sgst_name),
                                         ('company_id','=',res.id)])
            cgst_tax_id = AccountTax.search(['&',('name','=',cgst_name),
                                         ('company_id','=',res.id)])
            tax_id.tax_dest_id = sgst_tax_id.id
            FiscalPositionTax.create({
                                    'position_id' : fiscal_position_id.id,
                                    'tax_src_id' : tax_id.tax_src_id.id,
                                    'tax_dest_id' : cgst_tax_id.id})

#         add 0% taxes for inner state tax
        FiscalPositionTax.create({
                                'position_id' : fiscal_position_id.id,
                                'tax_src_id' : gst_sale_id.id,
                                'tax_dest_id' : sgst_sale_id.id})
        FiscalPositionTax.create({
                                'position_id' : fiscal_position_id.id,
                                'tax_src_id' : gst_sale_id.id,
                                'tax_dest_id' : cgst_sale_id.id})
        FiscalPositionTax.create({
                                'position_id' : fiscal_position_id.id,
                                'tax_src_id' : gst_purchase_id.id,
                                'tax_dest_id' : sgst_purchase_id.id})
        FiscalPositionTax.create({
                                'position_id' : fiscal_position_id.id,
                                'tax_src_id' : gst_purchase_id.id,
                                'tax_dest_id' : cgst_purchase_id.id})

#         add 0% taxes for outer state tax 
        FiscalPositionTax.create({
                                'position_id' : outer_position_id.id,
                                'tax_src_id' : gst_purchase_id.id,
                                'tax_dest_id' : igst_purchase_id.id})
        FiscalPositionTax.create({
                                'position_id' : outer_position_id.id,
                                'tax_src_id' : gst_sale_id.id,
                                'tax_dest_id' : igst_sale_id.id})

        return res

    @api.multi
    def write(self,vals):
        users = self.env['res.users'].search(['|',('name','=',self.name + ' Manager'),
                                                  ('name','=',self.name + ' User')])
        if vals.get('name'):
            for user in users:
                if 'Manager' in user.name:
                    user.name = vals['name'] + ' Manager'
                    user.login = vals['name'] + ' manager'
                else:
                    user.name = vals['name'] + ' User'
                    user.login = vals['name'] + ' user'

        return super(Company,self).write(vals)


class ResPartnerInh(models.Model):
    _inherit = 'res.partner'

    customer_id = fields.Char('Customer ID')

