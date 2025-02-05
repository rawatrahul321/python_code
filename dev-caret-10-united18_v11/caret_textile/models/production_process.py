# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import math
import datetime

class ProductionProcess(models.Model):
    _name = 'production.process'
    _description = 'Production'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'product_id'

    #COMMON
    name = fields.Char('Design Number')
    inward_material_id = fields.Many2one('inward.material',string='Inward Material',copy=False)
    product_id = fields.Many2one('product.product',string='Fabric Product',copy=False)
    product_uom_id = fields.Many2one('product.uom',string='UOM',copy=False)
    product_category_id = fields.Many2one('product.category',string='Product Category',copy=False)
    size_attribute_ids = fields.Many2many('size.size',string='Size',copy=False)
    colour_attribute_ids = fields.Many2many('color.color',string='Colour',copy=False)
    available_qty = fields.Float(string='Available Qty',copy=False)
    process_qty = fields.Float(string='Process Qty',copy=False)
    process_uom_id = fields.Many2one('product.uom',string='Process UOM',copy=False)
    process_method = fields.Selection([
        ('full', 'Full'),
        ('partial', 'Partial'),
        ], string='Process', copy=False, index=True, track_visibility='onchange', default='full')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    worksheet = fields.Binary('PDF')
    accessory_ids = fields.One2many('accessory.accessory','process_id',string='Accessories')
    final_accessory_cost = fields.Float(compute='_final_accessory_cost', string="Total Accessory Cost", store=True)
    state = fields.Selection([
        ('design', 'Designing'),
        ('cutting', 'Cutting'),
        ('stitching', 'Stitching'),
        ('washing', 'Washing'),
        ('finishing', 'Finishing'),
        ('qa', 'QA'),
        ('done','Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='design')

    #DESIGN FIELDS
    inward_location_id = fields.Many2one('stock.location',string='Inward Location',copy=False)
    cutting_location_id = fields.Many2one('stock.location',string='Cutting & Stitching Location',copy=False)
    cutting_jober_id = fields.Many2one('res.users',string='Cutting/Stitching Jober',default=lambda self: self.env.user)

    # CUTTING FIELDS
    cutting_order_ids = fields.One2many('cutting.normal.order','process_id',string='Cuttingline',copy=False)
    total_cutting_produced_qty = fields.Float(compute='_total_cost_for_cutting', string="Total Cutting Qty", store=True)
    cutting_cost_per_unit = fields.Float(string='Cost Per Piece',copy=False)
    total_cutting_cost = fields.Float(compute='_total_cost_for_cutting', string="Total Cutting Cost", store=True)
    fabric_color_type = fields.Selection([
        ('color', 'Color'),
        ('noncolor', 'Non-Color'),
        ], string='Fabric Color Type', copy=False, index=True,default='color')

    # STITCHING FIELDS
    joborder_ids = fields.One2many('stitching.normal.order','process_id',string='Stitchingline',copy=False)
    jobwork_ids = fields.One2many('stitching.job.work','process_id',string='Job Work',copy=False)
    state = fields.Selection([
        ('design', 'Designing'),
        ('cutting', 'Cutting'),
        ('stitching', 'Stitching'),
        ('washing', 'Washing'),
        ('finishing', 'Finishing'),
        ('qa', 'QA'),
        ('done','Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='design')
    stitching_type = fields.Selection([
        ('normal', 'Normal'),
        ('jobwork', 'Jobwork'),
        ], string='Stitching Type', copy=False, index=True, track_visibility='onchange', default='normal')
    total_stitching_cost = fields.Float(compute='_total_cost_for_stitching', string="Stitching Cost", store=True)
    total_jobwork_cost = fields.Float(compute='_total_cost_for_stitching', string="Jobwork Cost", store=True)
    total_cost_stitching = fields.Float(compute='_total_cost_for_stitching', string="Total Cost", store=True)
    cost_per_unit = fields.Float(string='Cost Per Piece',copy=False)
    washing_location_id = fields.Many2one('stock.location',string='Washing GODOWN',copy=False)
    washing_jober_id = fields.Many2one('res.users',string='Washing Jober')
    total_produced_qty = fields.Float(compute='_total_cost_for_stitching', string="Produced Qty", store=True)
    average_per_meter = fields.Float(compute='_total_cost_for_stitching', string="Avg Per Meter", store=True)
    product_template_id = fields.Many2one('product.template',string='Product Template',copy=False)

    #WASHING FIELDS
    washing_ids = fields.One2many('washing.production.line','washing_order_id',string='Produced Piece',copy=False)
    washing_colour_ids = fields.One2many('washing.produced.line','colour_washing_id',string='Colour',copy=False)
    total_washing_produced_qty = fields.Float(compute='_total_washing_produced_qty', string="Total Washing Produced Qty", store=True)
    washing_cost_per_unit = fields.Float(string='Washing Cost Per Piece',copy=False)
    total_washing_cost = fields.Float(compute='_total_washing_produced_qty', string="Total Washing Cost", store=True)

    finishing_jober_id = fields.Many2one('res.users',string='Finishing Jober',copy=False)
    finishing_location_id = fields.Many2one('stock.location',string='Finishing GODOWN',copy=False)

    #FINISHING FIELDS
    finishing_ids = fields.One2many('finishing.order.line','finishing_order_id',string='Finishing Lines',copy=False)
    finishing_colour_ids = fields.One2many('finishing.produced.line','finishing_process_id',string='Finishing',copy=False)
    total_actual_finished_qty = fields.Float(compute='_total_actual_finished_qty', string="Total Actual Finished Qty", store=True)
    article_number = fields.Char('Article Number',copy=False)
    qa_id = fields.Many2one('res.users',string='QA Responsible',copy=False)
    final_location_id = fields.Many2one('stock.location',string='Final Stock GODOWN')
    finishing_cost_per_unit = fields.Float(string='Finishing Cost Per Piece',copy=False)
    total_finishing_cost = fields.Float(compute='_total_finishing_cost', string="Total Finishing Cost", store=True)

    #Costing Fields
    total_overall_costing = fields.Float(compute='_total_overall_costing', string="Total Overall Costing", store=True)
    mrp_per_unit = fields.Float(compute='_total_overall_costing', string="MRP", store=True)

    #EXTRA INVOICES
    invoice_ids = fields.Many2many("account.invoice", string='Jober Invoices', readonly=True, copy=False)
    stock_move_ids = fields.Many2many("stock.move", string='Stock Moves', readonly=True, copy=False)

    @api.multi
    @api.depends('total_actual_finished_qty','finishing_cost_per_unit')
    def _total_finishing_cost(self):
        TotalFinishCost = 0.0
        for finishing in self:
            total = finishing.total_actual_finished_qty * finishing.finishing_cost_per_unit
            TotalFinishCost += total
            finishing.total_finishing_cost = TotalFinishCost
            
    @api.multi
    def action_view_invoice(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree2')
        result = action.read()[0]
        if len(self.invoice_ids) > 1:
            result['domain'] = "[('id', 'in', %s)]" % self.invoice_ids.ids
        else:
            form_view = self.env.ref('account.invoice_supplier_form')
            result['views'] = [(form_view.id, 'form')]
            result['res_id'] = self.invoice_ids.id
        return result
    
    @api.multi
    def action_view_stock_moves(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_action')
        result = action.read()[0]
        if len(self.stock_move_ids) > 1:
            result['domain'] = "[('id', 'in', %s)]" % self.stock_move_ids.ids
        else:
            form_view = self.env.ref('stock.view_move_form')
            result['views'] = [(form_view.id, 'form')]
            result['res_id'] = self.stock_move_ids.id
        return result

    @api.multi
    def create_invoices(self,name,qty,cost_per_unit,invoice_id,product_id):
        ProductId = self.env['product.product'].search([],limit=1)
        if product_id:
            product=product_id.id
        else:
            product=False
        self.env['account.invoice.line'].create({
            'product_id': product,
            'quantity': qty or 0.0,
            'price_unit': cost_per_unit or 0.0,
            'invoice_id': invoice_id.id,
            'name': name or '',
            'account_id': (product_id.property_account_expense_id.id or product_id.categ_id.property_account_expense_categ_id.id) or (ProductId.property_account_expense_id.id or ProductId.categ_id.property_account_expense_categ_id.id),
        })
        invoice_id._onchange_invoice_line_ids()
        return invoice_id

    @api.multi
    @api.depends('total_cutting_cost','total_cost_stitching','total_washing_cost','final_accessory_cost','total_actual_finished_qty')
    def _total_overall_costing(self):
        for order in self:
            order.total_overall_costing = order.total_cutting_cost + order.total_cost_stitching + order.total_washing_cost + order.final_accessory_cost
            if order.total_actual_finished_qty > 0.0:
                order.mrp_per_unit = order.total_overall_costing / order.total_actual_finished_qty
            else:
                order.mrp_per_unit = 0.0

    @api.model
    def _get_default_uom(self):
        ProductUomObj = self.env['product.uom']
        UOMId = ProductUomObj.search([('name','in',('Piece','Unit(s)'))],limit=1)
        return UOMId and UOMId.id or False

    @api.multi
    @api.depends('cutting_order_ids.size_qty','cutting_cost_per_unit')
    def _total_cost_for_cutting(self):
        TotalCost = 0.0
        for order in self:
            for cutting in order.cutting_order_ids:
                self.total_cutting_produced_qty += cutting.size_qty
            if order.cutting_cost_per_unit > 0.0:
                Subtotal = order.total_cutting_produced_qty * order.cutting_cost_per_unit
                TotalCost += Subtotal
                order.total_cutting_cost = TotalCost

    @api.multi
    @api.depends('process_qty','joborder_ids.size_qty','cost_per_unit','jobwork_ids.total_cost')
    def _total_cost_for_stitching(self):
        TotalCost = 0.0
        for joborder in self.joborder_ids:
            self.total_produced_qty += joborder.size_qty
        for jobwork in self.jobwork_ids:
            self.total_jobwork_cost += jobwork.total_cost    
            TotalCost += jobwork.total_cost
        if self.cost_per_unit > 0.0:
            self.total_stitching_cost = self.total_produced_qty * self.cost_per_unit
            TotalCost += self.total_stitching_cost
        else:
            self.total_stitching_cost = 0.0
            TotalCost += self.total_stitching_cost
        self.total_cost_stitching = TotalCost
        if self.total_produced_qty > 0.0:
            self.average_per_meter = self.process_qty / self.total_produced_qty
        else:
            self.average_per_meter = 0.0

    @api.multi
    def create_stock_moves(self,product,uom,location_id,location_dest_id,qty,lot):
        StockMoveObj = self.env['stock.move']
        StockMoveDict = {
             'name': product.name or '/',
             'location_id': location_id and location_id.id or False,
             'location_dest_id': location_dest_id and location_dest_id.id or False,
             'product_id': product and product.id or False,
             'product_uom': uom and uom.id or False,
             'product_uom_qty': qty or 0.0, 
             'origin': product.name or '',
             'reference': product.name or '',
             }
        StockMove = StockMoveObj.create(StockMoveDict)
        StockMove._action_confirm()
        StockMove._action_assign()
        StockMove.move_line_ids.write({'qty_done':qty or 0.0,'lot_id':lot and lot.id or False})
        StockMove._action_done()
        self.stock_move_ids = [(4, StockMove.id, None)]
        return StockMove

    @api.multi
    def action_send_to_cutting(self):
        StockMoveObj = self.env['stock.move']
        for production in self:
            StockMove = production.create_stock_moves(production.product_id,
                                                      production.product_uom_id,
                                                      production.inward_location_id,
                                                      production.cutting_location_id,
                                                      production.process_qty,
                                                      lot=False)
            print ("Stock move for Cutting********************",StockMove)
            production.state = 'cutting'
            return True

    @api.multi
    def action_send_to_stitching(self):
        StitchingNormalOrderObj = self.env['stitching.normal.order']
        ProductTemplateObj = self.env['product.template']
        ProductProductObj = self.env['product.product']
        ProductAttributeValueObj = self.env['product.attribute.value']
        ProductAttributeLineObj = self.env['product.attribute.line']
        StockMoveObj = self.env['stock.move']
        AttributeLines = []
        VariantIds = []
        UnitUOM = self.env.ref('product.product_uom_unit')
        for production in self:
            SupplierId = self.env['res.partner'].browse(1)
            invoice_id = self.env['account.invoice'].create({
                'partner_id': SupplierId and SupplierId.id or False,
                'currency_id': self.env.ref('base.INR').id,
                'name': production.name + production.state,
                'account_id': SupplierId.property_account_payable_id and SupplierId.property_account_payable_id.id,
                'type': 'in_invoice',
                'date_invoice': datetime.datetime.today(),
                'origin': production.name + production.state,
            })

            ProductTemplateDict = {
                 'name': production.name or '',
                 'type': 'product',
                 'uom_id': UnitUOM and UnitUOM.id or False,
                 'qty_available': 0.0,
                 'categ_id': production.product_category_id and production.product_category_id.id or False,
                 }
            ProductTemplateId = ProductTemplateObj.create(ProductTemplateDict)
            SizeAttributeID = self.env.ref('caret_textile.product_attribute_size')
            ColorAttributeID = self.env.ref('caret_textile.product_attribute_color')
            SizeLine = ProductAttributeLineObj.search([('attribute_id','=',SizeAttributeID.id),
                                                       ('product_tmpl_id','=',ProductTemplateId.id)],limit=1)
            print ("SizeLine&&&&&&&&&&&&&&&&&&&&",SizeLine)
            if not SizeLine:
                SizeLine = ProductAttributeLineObj.create({'attribute_id':SizeAttributeID.id,
                                                           'product_tmpl_id':ProductTemplateId and ProductTemplateId.id or False})
                print ("SizeLine&&&&&&&eELSE&&&&&&&&&&&&&",SizeLine)

            ColorLine = ProductAttributeLineObj.search([('attribute_id','=',ColorAttributeID.id),
                                                        ('product_tmpl_id','=',ProductTemplateId.id)],limit=1)
            print ("ColorLine&&&&&&&&&&&&&&&&&&&&",ColorLine)
            if not ColorLine:
                ColorLine = ProductAttributeLineObj.create({'attribute_id':ColorAttributeID.id,
                                                            'product_tmpl_id':ProductTemplateId and ProductTemplateId.id or False})
                print ("ColorLine&&&&&&&&&&&&&&&&&&&&",ColorLine)

            PRODUCTS = []
            Count = 1
            ProductId = False
            SizeValues = []
            ColorValues = []
            for cuttingline in production.cutting_order_ids:
                ATTRIBUTES = []
                SearchAttributeId = ProductAttributeValueObj.search([('name','=',cuttingline.size_id.name),
                                                                     ('attribute_id','=',SizeAttributeID.id)]
                                                                    )
                if not SearchAttributeId:
                    SearchAttributeId = ProductAttributeValueObj.create({'name':cuttingline.size_id.name,
                                                                         'attribute_id':SizeAttributeID.id})
                
                ATTRIBUTES.append(SearchAttributeId.id)
                if cuttingline.color_id:
                    SearchColorAttributeId = ProductAttributeValueObj.search([('name','=',cuttingline.color_id.name),
                                                                         ('attribute_id','=',ColorAttributeID.id)])
                    if not SearchColorAttributeId:
                        SearchColorAttributeId = ProductAttributeValueObj.create({'name':cuttingline.color_id.name,
                                                                        'attribute_id':ColorAttributeID.id})

                    ATTRIBUTES.append(SearchColorAttributeId.id)
                    if SearchColorAttributeId.id not in ColorValues:
                        ColorValues.append(SearchColorAttributeId.id)
                if SearchAttributeId.id not in SizeValues:
                    SizeValues.append(SearchAttributeId.id)
                
                if Count == 1:
                    ProductId = ProductTemplateId.product_variant_ids[0]
                    ProductId.attribute_value_ids = [(6, 0, ATTRIBUTES)]
                    print ("ProductId********If**********",ProductId)
                else:
                    ProductVariantDict = {
                        'product_tmpl_id': ProductTemplateId and ProductTemplateId.id or False,
                        'name': production.name or '',
                        'type': 'product',
                        'uom_id': UnitUOM and UnitUOM.id or False,
                        'qty_available': 0.0,
                        'attribute_value_ids': [(6, 0, ATTRIBUTES)],
                        'categ_id': production.product_category_id and production.product_category_id.id or False,
                    }
                    ProductId = ProductProductObj.create(ProductVariantDict)
                    print ("ProductId*******Else***********",ProductId)

                cuttingline.product_id = ProductId and ProductId.id or False

                production.create_stock_moves(ProductId,
                                              ProductId.uom_id,
                                              production.cutting_location_id,
                                              production.cutting_location_id,
                                              cuttingline.size_qty,
                                              lot=False)

                production.create_invoices(cuttingline.size_id.name,cuttingline.size_qty,production.cutting_cost_per_unit,invoice_id,product_id=ProductId)
                
                PRODUCTS.append((0,0,{
                     'product_id': ProductId and ProductId.id or False,
                     'size_id': cuttingline.size_id and cuttingline.size_id.id or False,
                     'size_qty': cuttingline.size_qty or 0.0,
                     'company_id':cuttingline.company_id and cuttingline.company_id.id or False,
                     'process_id': cuttingline.process_id and cuttingline.process_id.id or False,
                     'product_uom_id': cuttingline.product_uom_id and cuttingline.product_uom_id.id or False,
                     'color_id': cuttingline.color_id and cuttingline.color_id.id or False,
                     }))
                Count += 1
            SizeLine.value_ids = [(6, 0, SizeValues)]
            ColorLine.value_ids = [(6, 0, ColorValues)]
            production.joborder_ids = PRODUCTS
            production.product_template_id = ProductTemplateId and ProductTemplateId.id or False
            production.state = 'stitching'
            production.invoice_ids = [(4, invoice_id.id, None)]
            return True

    @api.multi
    def action_send_to_washing(self):
        WashingLineObj = self.env['washing.production.line']
        StockMoveObj = self.env['stock.move']
        AttributeLines = []
        VariantIds = []
        UnitUOM = self.env.ref('product.product_uom_unit')
        for production in self:
            if not production.joborder_ids or not production.cost_per_unit:
                raise UserError(_("Please Check Stitching Details with Size and Qty and Cost Per Piece Added !"))
            if not production.washing_jober_id or not production.washing_location_id:
                raise UserError(_("Please Add Washing Jober and Washing Location !"))

            SupplierId = self.env['res.partner'].browse(1)
            invoice_id = self.env['account.invoice'].create({
                'partner_id': SupplierId and SupplierId.id or False,
                'currency_id': self.env.ref('base.INR').id,
                'name': production.name + production.state,
                'account_id': SupplierId.property_account_payable_id and SupplierId.property_account_payable_id.id,
                'type': 'in_invoice',
                'date_invoice': datetime.datetime.today(),
                'origin': production.name + production.state,
            })
            for jobline in production.joborder_ids:
                StockMove = production.create_stock_moves(jobline.product_id,
                                                          jobline.product_id.uom_id,
                                                          production.cutting_location_id,
                                                          production.washing_location_id,
                                                          jobline.size_qty,
                                                          lot=False)
                print ("Stock move for Send TO Washing********************",StockMove)
                production.create_invoices(jobline.product_id.name,jobline.size_qty,production.cost_per_unit,invoice_id,product_id=jobline.product_id)
                WashingProductionLineDict = {
                    'washing_order_id':production and production.id or False,
                    'product_id': jobline.product_id and jobline.product_id.id or False,
                    'uom_id': jobline.product_id.uom_id and jobline.product_id.uom_id.id or False,
                    'location_id': production.washing_location_id and production.washing_location_id.id or False,
                    'process_qty': jobline.size_qty or 0.0,
                    'actual_received_qty': jobline.size_qty or 0.0,
                    'color_id': jobline.color_id and jobline.color_id.id or False,
                    'size_id': jobline.size_id and jobline.size_id.id or False,
                    }
                Washingline = WashingLineObj.create(WashingProductionLineDict)
                print ("Washingline******************",Washingline)
            for jobwork in production.jobwork_ids:
                production.create_invoices(jobwork.product_id.name,production.total_produced_qty,jobwork.cost_per_piece,invoice_id,product_id=jobwork.product_id)
            production.state = 'washing'
            production.invoice_ids = [(4, invoice_id.id, None)]
            return True

    @api.multi
    def action_send_to_finishing(self):
        StockMoveObj = self.env['stock.move']
        ProductObj = self.env['product.product']
        ProductAttributeValue = self.env['product.attribute.value']
        ProductAttributeLineObj = self.env['product.attribute.line']
        AttributeLines = []
        ValueIds = []
        VariantIds = []
        UOM = False
        SizeAttributeID = self.env.ref('caret_textile.product_attribute_size')
        ColorAttributeID = self.env.ref('caret_textile.product_attribute_color')
        #ColorAttributeID = self.env.ref('caret_textile.product_attribute_color')
        for production in self:
            if not production.finishing_location_id:
                raise UserError(_("Please Add Finishing Location !"))
            FINISHPRODUCTION = []

            SupplierId = self.env['res.partner'].browse(1)
            invoice_id = self.env['account.invoice'].create({
                'partner_id': SupplierId and SupplierId.id or False,
                'currency_id': self.env.ref('base.INR').id,
                'name': production.name + production.state,
                'account_id': SupplierId.property_account_payable_id and SupplierId.property_account_payable_id.id,
                'type': 'in_invoice',
                'date_invoice': datetime.datetime.today(),
                'origin': production.name + production.state,
            })

            if production.fabric_color_type == 'color' or (production.fabric_color_type == 'noncolor' and not production.washing_colour_ids):
                for washing in production.washing_ids:
                    StockMove = production.create_stock_moves(washing.product_id,
                                                              washing.product_id.uom_id,
                                                              production.washing_location_id,
                                                              production.finishing_location_id,
                                                              washing.actual_received_qty,
                                                              lot=False)
                    print ("Stock move for Send TO Finishing*******IF*************",StockMove)
                    FINISHPRODUCTION.append((0,0,{
                        'product_id': washing.product_id and washing.product_id.id or False,
                        'uom_id': washing.product_id.uom_id and washing.product_id.uom_id.id or False,
                        'location_id': production.finishing_location_id and production.finishing_location_id.id or False,
                        'process_qty': washing.actual_received_qty or 0.0,
                        'actual_received': washing.actual_received_qty or 0.0,
                        'color_id': washing.color_id and washing.color_id.id or False,
                        'size_id': washing.size_id and washing.size_id.id or False,
                        }))
                    production.create_invoices(washing.product_id.name,washing.actual_received_qty,production.washing_cost_per_unit,invoice_id,washing.product_id)

            elif production.fabric_color_type == 'noncolor' and production.washing_colour_ids:
                print ("NON Color Condition*************************")
                NewWashingProductTemplate = production.product_template_id.copy()
                print ("NewWashingProductTemplate**************",NewWashingProductTemplate)
                SizeValues = []
                ColorValues = []
                SizeLine = ProductAttributeLineObj.search([('attribute_id','=',SizeAttributeID.id),
                                                           ('product_tmpl_id','=',NewWashingProductTemplate.id)],limit=1)

                if not SizeLine:
                    SizeLine = ProductAttributeLineObj.create({'attribute_id':SizeAttributeID.id,
                                                               'product_tmpl_id':NewWashingProductTemplate and NewWashingProductTemplate.id or False})
        
                ColorLine = ProductAttributeLineObj.search([('attribute_id','=',ColorAttributeID.id),
                                                            ('product_tmpl_id','=',NewWashingProductTemplate.id)],limit=1)
                if not ColorLine:
                    ColorLine = ProductAttributeLineObj.create({'attribute_id':ColorAttributeID.id,
                                                                'product_tmpl_id':NewWashingProductTemplate and NewWashingProductTemplate.id or False})
                for wash in production.washing_colour_ids:
                    # Add Color in Product Attribute
                    ATTRIBUTES = []
                    if not wash.colour_id:
                        raise UserError(_("Please Add Color Because You have Added Colouring Detail!"))

                    SearchAttributeId = ProductAttributeValue.search([('name','=',wash.size_id.name),
                                                                      ('attribute_id','=',SizeAttributeID.id)])
                    if not SearchAttributeId:
                        SearchAttributeId = ProductAttributeValueObj.create({'name':wash.size_id.name,
                                                                             'attribute_id':SizeAttributeID.id})
                    ATTRIBUTES.append(SearchAttributeId.id)

                    if SearchAttributeId.id not in SizeValues:
                        SizeValues.append(SearchAttributeId.id)
    
                    SearchColorAttributeId = ProductAttributeValue.search([('attribute_id','=',ColorAttributeID.id),
                                                                           ('name','=',wash.colour_id.name)])

                    if not SearchColorAttributeId:
                        SearchColorAttributeId = ProductAttributeValue.create({'attribute_id':ColorAttributeID and ColorAttributeID.id or False,
                                                                               'name': wash.colour_id and wash.colour_id.name or False})
                    ATTRIBUTES.append(SearchColorAttributeId.id)

                    if SearchColorAttributeId.id not in ColorValues:
                        ColorValues.append(SearchColorAttributeId.id)

                    NewWashingProduct = wash.product_id.copy(default={'product_tmpl_id':NewWashingProductTemplate.id,
                                                                      'attribute_value_ids':[(6, 0, ATTRIBUTES)]})
                    
                    print ("OLD AND NEW PRODUCT**************************",wash.product_id,NewWashingProduct,NewWashingProduct.attribute_value_ids)
                    #NewWashingProduct.attribute_value_ids = [(4,colour_id)]
                    print ("Updated Attrib*******************",wash.product_id,wash.product_id.attribute_value_ids)
                    #Create Stock Moves
                    StockMove = production.create_stock_moves(NewWashingProduct,
                                                              wash.uom_id,
                                                              production.washing_location_id,
                                                              production.finishing_location_id,
                                                              wash.colour_qty,
                                                              lot=False)
                    print ("Stock move for Send TO Finishing********ELSE************",StockMove)
                    production.create_invoices(NewWashingProduct.name,wash.colour_qty,production.washing_cost_per_unit,invoice_id,wash.product_id)
                    FINISHPRODUCTION.append((0,0,{
                        'product_id': NewWashingProduct and NewWashingProduct.id or False,
                        'uom_id': wash.uom_id and wash.uom_id.id or False,
                        'location_id': production.finishing_location_id and production.finishing_location_id.id or False,
                        'process_qty': wash.colour_qty or 0.0,
                        'actual_received': wash.colour_qty or 0.0,
                        'color_id': wash.colour_id and wash.colour_id.id or False,
                        'size_id': wash.size_id and wash.size_id.id or False,
                        }))
                    wash.product_id = NewWashingProduct and NewWashingProduct.id or False
                print ("SizeValues**************",SizeValues)
                print ("ColorValues**************",ColorValues)
                SizeLine.value_ids = [(6, 0, SizeValues)]
                ColorLine.value_ids = [(6, 0, ColorValues)]
            production.finishing_ids = FINISHPRODUCTION
            production.state = 'finishing'
            production.invoice_ids = [(4, invoice_id.id, None)]
            return True

    @api.onchange('washing_jober_id')
    def _onchange_washing_jober_id(self):
        StockLocationObj = self.env['stock.location']
        if self.washing_jober_id:
            ParetnLocationId = self.env.ref('stock.stock_location_locations_virtual')
            GODown = StockLocationObj.search([('name','=',self.washing_jober_id.name),
                                              ('partner_id','=',self.washing_jober_id.partner_id and self.washing_jober_id.partner_id.id or False),
                                              ('location_id','=',ParetnLocationId and ParetnLocationId.id or False),
                                              ('usage','=','production')],limit=1)
            if GODown:
                self.washing_location_id = GODown and GODown.id or False
            else:
                self.washing_location_id = StockLocationObj.create({'name':self.washing_jober_id.name,
                                                                  'partner_id': self.washing_jober_id.partner_id and self.washing_jober_id.partner_id.id or False,
                                                                  'usage':'production',
                                                                  'location_id':ParetnLocationId and ParetnLocationId.id or False,
                                                                  })

    @api.onchange('finishing_jober_id')
    def _onchange_finishing_jober_id(self):
        StockLocationObj = self.env['stock.location']
        if self.finishing_jober_id:
            ParetnLocationId = self.env.ref('stock.stock_location_locations_virtual')
            GODown = StockLocationObj.search([('name','=',self.finishing_jober_id.name),
                                              ('partner_id','=',self.finishing_jober_id.partner_id and self.finishing_jober_id.partner_id.id or False),
                                              ('location_id','=',ParetnLocationId and ParetnLocationId.id or False),
                                              ('usage','=','production')],limit=1)
            if GODown:
                self.finishing_location_id = GODown and GODown.id or False
            else:
                self.finishing_location_id = StockLocationObj.create({'name':self.finishing_jober_id.name,
                                                                  'partner_id': self.finishing_jober_id.partner_id and self.finishing_jober_id.partner_id.id or False,
                                                                  'usage':'production',
                                                                  'location_id':ParetnLocationId and ParetnLocationId.id or False,
                                                                  })

    @api.multi
    @api.depends('accessory_ids.total_accessory_cost','total_actual_finished_qty')
    def _final_accessory_cost(self):
        FinalAccessoryCost = 0.0
        for final in self:
            for accessory in final.accessory_ids:
                FinalAccessoryCost += accessory.total_accessory_cost
            final.final_accessory_cost = FinalAccessoryCost * final.total_actual_finished_qty

    @api.multi
    @api.depends('finishing_ids.actual_received','finishing_colour_ids.colour_qty')
    def _total_actual_finished_qty(self):
        TotalFinishedQty = 0.0
        for finishing in self:
            if finishing.fabric_color_type == 'noncolor' and not finishing.finishing_ids:
                for finishcustomorder in finishing.finishing_colour_ids:
                    TotalFinishedQty += finishcustomorder.colour_qty
            else:
                for finishorder in finishing.finishing_ids:
                    TotalFinishedQty += finishorder.actual_received
            finishing.total_actual_finished_qty = TotalFinishedQty


    @api.multi
    @api.depends('washing_ids.actual_received_qty','washing_colour_ids.colour_qty','washing_cost_per_unit')
    def _total_washing_produced_qty(self):
        TotalWashingQty = 0.0
        TotalCost = 0.0
        for washing in self:
            if washing.fabric_color_type == 'noncolor' and not washing.washing_ids:
                for joborder in washing.washing_colour_ids:
                    TotalWashingQty += joborder.colour_qty 
                washing.total_washing_produced_qty = TotalWashingQty
                if washing.washing_cost_per_unit > 0.0:
                    Subtotal = washing.total_washing_produced_qty * washing.washing_cost_per_unit
                    TotalCost += Subtotal
                    washing.total_washing_cost = TotalCost
            else:
                for joborder in washing.washing_ids:
                    TotalWashingQty += joborder.actual_received_qty
                washing.total_washing_produced_qty = TotalWashingQty
                if washing.washing_cost_per_unit > 0.0:
                    Subtotal = washing.total_washing_produced_qty * washing.washing_cost_per_unit
                    TotalCost += Subtotal
                    washing.total_washing_cost = TotalCost

    @api.multi
    def action_send_to_designer(self):
        for production in self:
            production.state = 'design'
            return True

    @api.onchange('cutting_jober_id')
    def _onchange_cutting_jober_id(self):
        StockLocationObj = self.env['stock.location']
        if self.cutting_jober_id:
            ParetnLocationId = self.env.ref('stock.stock_location_locations_virtual')
            GODown = StockLocationObj.search([('name','=',self.cutting_jober_id.name),
                                              ('partner_id','=',self.cutting_jober_id.partner_id and self.cutting_jober_id.partner_id.id or False),
                                              ('location_id','=',ParetnLocationId and ParetnLocationId.id or False),
                                              ('usage','=','production')],limit=1)
            if GODown:
                self.cutting_location_id = GODown and GODown.id or False
            else:
                self.cutting_location_id = StockLocationObj.create({'name':self.cutting_jober_id.name,
                                                                  'partner_id': self.cutting_jober_id.partner_id and self.cutting_jober_id.partner_id.id or False,
                                                                  'usage':'production',
                                                                  'location_id':ParetnLocationId and ParetnLocationId.id or False,
                                                                  })

    @api.model
    def create(self, vals):
        USER = self.env['res.users'].browse(vals.get('cutting_jober_id'))
        ProductCategory = self.env['product.category'].browse(vals.get('product_category_id'))
        CurrentYear = int(datetime.datetime.now().year)
        CurrentYrLstTwoDigits = str(CurrentYear)[2:]
        if 'company_id' in vals:
            vals['name'] = USER.name[:1] + ProductCategory.name[:1] + CurrentYrLstTwoDigits + '/' + self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('production.process') or _('New')
        else:
            vals['name'] = USER.name[:1] + ProductCategory.name[:1] + CurrentYrLstTwoDigits + '/' + self.env['ir.sequence'].next_by_code('production.process') or _('New')
        return super(ProductionProcess, self).create(vals)

    @api.onchange('inward_material_id','product_id','process_method')
    def _onchange_material_product_id(self):
        if self.inward_material_id:
            self.product_id = self.inward_material_id.product_id and self.inward_material_id.product_id.id or False
            self.available_qty = self.inward_material_id.product_id.qty_available or 0.0
            self.inward_location_id = self.inward_material_id.location_id and self.inward_material_id.location_id.id or False
            self.product_uom_id = self.product_id.uom_id and self.product_id.uom_id.id or False
            if self.process_method == 'full':
                self.process_qty = self.available_qty
            else:
                self.process_qty = 0.0
        else:
            self.available_qty = self.product_id.qty_available or 0.0
            self.product_uom_id = self.product_id.uom_id and self.product_id.uom_id.id or False
            if self.process_method == 'full':
                self.process_qty = self.available_qty
            else:
                self.process_qty = 0.0

    @api.multi
    def write(self,vals):
        UserObj = self.env['res.users']
        for production in self:
            if vals.get('cutting_jober_id') and production.state in ('design','cutting','stitching'):
                CuttingJober = UserObj.browse(vals.get('cutting_jober_id'))
                Name = production.name
                vals['name'] =Name.replace(Name[:2],CuttingJober.name[:2])
            if production.fabric_color_type == 'color' or (production.fabric_color_type == 'noncolor' and len(self.finishing_colour_ids) < 1):
                for final in self.finishing_ids:
                    print ("vals article****************",vals.get('article_number'),"Article number**************",self.article_number,"Final lot in Line",final.lot_id.name)
                    if vals.get('article_number') and not final.lot_id:
                        Sequence = self.env['ir.sequence'].next_by_code('stock.barcode.serial')
                        ArticleNumber = vals.get('article_number') or ''
                        Color = final.color_id and final.color_id.name or ''
                        Size = final.size_id and final.size_id.name or ''
                        NEWLOTID = self.env['stock.production.lot'].create({'name':ArticleNumber +'/'+ Size + Color + '/' + Sequence,
                                                                            'product_id':final.product_id and final.product_id.id or False,
                                                                                })
                        final.lot_id = NEWLOTID and NEWLOTID.id or False
                    elif vals.get('article_number') and final.lot_id:
                        SplitedOldLot = (final.lot_id.name).split("/", 1)
                        final.lot_id.name = vals.get('article_number')+ '/' + SplitedOldLot[1]
            elif (production.fabric_color_type == 'noncolor' and len(self.finishing_colour_ids) > 0) or (production.fabric_color_type == 'noncolor' and not self.finishing_ids):
                for final in self.finishing_colour_ids:
                    print ("vals article****************",vals.get('article_number'),"Article number**************",self.article_number,"Final lot in Line",final.lot_id.name)
                    if vals.get('article_number') and not final.lot_id:
                        Sequence = self.env['ir.sequence'].next_by_code('stock.barcode.serial')
                        ArticleNumber = vals.get('article_number') or ''
                        Color = final.colour_id and final.colour_id.name or ''
                        Size = final.size_id and final.size_id.name or ''
                        NEWLOTID = self.env['stock.production.lot'].create({'name':ArticleNumber +'/'+ Size + Color + '/' + Sequence,
                                                                            'product_id':final.product_id and final.product_id.id or False,
                                                                                })
                        final.lot_id = NEWLOTID and NEWLOTID.id or False
                    elif vals.get('article_number') and final.lot_id:
                        SplitedOldLot = (final.lot_id.name).split("/", 1)
                        final.lot_id.name = vals.get('article_number')+ '/' + SplitedOldLot[1]
        return super(ProductionProcess,self).write(vals)

    @api.multi
    def action_send_to_qa(self):
        if not self.article_number:
            raise UserError(_("Please Add Article Number !"))
        self.state = 'qa'
        return True

    @api.multi
    def action_send_to_approve(self):
        StockMoveObj = self.env['stock.move']
        ProductAttributeValue = self.env['product.attribute.value']
        ProductAttributeLineObj = self.env['product.attribute.line']
        SizeAttributeID = self.env.ref('caret_textile.product_attribute_size')
        ColorAttributeID = self.env.ref('caret_textile.product_attribute_color')
        SupplierId = self.env['res.partner'].browse(1)
        for production in self:
            invoice_id = self.env['account.invoice'].create({
                'partner_id': SupplierId and SupplierId.id or False,
                'currency_id': self.env.ref('base.INR').id,
                'name': production.name + production.state,
                'account_id': SupplierId.property_account_payable_id and SupplierId.property_account_payable_id.id,
                'type': 'in_invoice',
                'date_invoice': datetime.datetime.today(),
                'origin': production.name + production.state,
            })
            if production.fabric_color_type == 'color' or (production.fabric_color_type == 'noncolor' and not production.finishing_colour_ids):
                for joborder in production.finishing_ids:
                    StockMove = production.create_stock_moves(joborder.product_id,
                                                              joborder.uom_id,
                                                              production.finishing_location_id,
                                                              production.final_location_id,
                                                              joborder.actual_received,
                                                              joborder.lot_id)
                    print ("Stock move for Send TO Stock********IF************",StockMove)
                    production.create_invoices(joborder.product_id.name,joborder.actual_received,production.finishing_cost_per_unit,invoice_id,joborder.product_id)
                    joborder.product_id.barcode = joborder.lot_id.name
                    joborder.product_id.standard_price = joborder.mrp
            elif production.fabric_color_type == 'noncolor' and production.finishing_colour_ids:
                NewWashingProductTemplate = production.product_template_id.copy()
                print ("NewWashingProductTemplate**************",NewWashingProductTemplate)
                SizeValues = []
                ColorValues = []
                SizeLine = ProductAttributeLineObj.search([('attribute_id','=',SizeAttributeID.id),
                                                           ('product_tmpl_id','=',NewWashingProductTemplate.id)],limit=1)

                if not SizeLine:
                    SizeLine = ProductAttributeLineObj.create({'attribute_id':SizeAttributeID.id,
                                                               'product_tmpl_id':NewWashingProductTemplate and NewWashingProductTemplate.id or False})
        
                ColorLine = ProductAttributeLineObj.search([('attribute_id','=',ColorAttributeID.id),
                                                            ('product_tmpl_id','=',NewWashingProductTemplate.id)],limit=1)
                if not ColorLine:
                    ColorLine = ProductAttributeLineObj.create({'attribute_id':ColorAttributeID.id,
                                                                'product_tmpl_id':NewWashingProductTemplate and NewWashingProductTemplate.id or False})

                for joborder in production.finishing_colour_ids:
                    ATTRIBUTES = []
                    SearchAttributeId = ProductAttributeValue.search([('name','=',joborder.size_id.name),
                                                                      ('attribute_id','=',SizeAttributeID.id)])
                    if not SearchAttributeId:
                        SearchAttributeId = ProductAttributeValueObj.create({'name':joborder.size_id.name,
                                                                             'attribute_id':SizeAttributeID.id})
                    ATTRIBUTES.append(SearchAttributeId.id)

                    if SearchAttributeId.id not in SizeValues:
                        SizeValues.append(SearchAttributeId.id)

                    SearchColorAttributeId = ProductAttributeValue.search([('attribute_id','=',ColorAttributeID.id),
                                                                           ('name','=',joborder.colour_id.name)])

                    if not SearchColorAttributeId:
                        SearchColorAttributeId = ProductAttributeValue.create({'attribute_id':ColorAttributeID and ColorAttributeID.id or False,
                                                                               'name': joborder.colour_id and joborder.colour_id.name or False})
                    ATTRIBUTES.append(SearchColorAttributeId.id)

                    if SearchColorAttributeId.id not in ColorValues:
                        ColorValues.append(SearchColorAttributeId.id)

                    NewWashingProduct = joborder.product_id.copy(default={'product_tmpl_id':NewWashingProductTemplate.id,
                                                                      'attribute_value_ids':[(6, 0, ATTRIBUTES)]})
                    #NewWashingProduct.attribute_value_ids = [(4,SearchColorAttributeId.id)]
                    StockMove = production.create_stock_moves(NewWashingProduct,
                                                              joborder.uom_id,
                                                              production.finishing_location_id,
                                                              production.final_location_id,
                                                              joborder.colour_qty,
                                                              joborder.lot_id)
                    print ("Stock move for Send TO Stock********ELSE************",StockMove)
                    production.create_invoices(NewWashingProduct.name,joborder.colour_qty,production.finishing_cost_per_unit,invoice_id,NewWashingProduct)
                    NewWashingProduct.barcode = joborder.lot_id.name
                    NewWashingProduct.standard_price = joborder.mrp
                    joborder.product_id = NewWashingProduct and NewWashingProduct.id or False
                SizeLine.value_ids = [(6, 0, SizeValues)]
                ColorLine.value_ids = [(6, 0, ColorValues)]
            production.state = 'done'
            return True
