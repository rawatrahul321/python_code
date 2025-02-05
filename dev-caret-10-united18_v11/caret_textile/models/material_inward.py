# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import math
from datetime import datetime

class InwardMaterial(models.Model):
    _name = 'inward.material'
    _description = 'Inward Material'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.model
    def _get_default_uom(self):
        ProductUomObj = self.env['product.uom']
        UOMId = self.env.ref('product.product_uom_meter')
        if UOMId:
            return UOMId and UOMId.id or False
        else:
            UOMId = ProductUomObj.search([('name','in',('m','meter','Meter'))],limit=1)
            return UOMId and UOMId.id or False

    name = fields.Char(string='Name')
    number = fields.Char(string='Number')
    short_number = fields.Char(string='Short Number')
    rate = fields.Float(string='Rate')
    quantity = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('product.uom',string='UOM',default=_get_default_uom)
    supplier_id = fields.Many2one('res.partner',string='Supplier')
    location_id = fields.Many2one('stock.location',string='Location')
    product_id = fields.Many2one('product.product',string='Product',copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting Approval'),
        ('inward', 'Inward'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    invoice_ids = fields.Many2many("account.invoice", string='Invoices', readonly=True, copy=False)


    @api.model
    def create(self, vals):
        if vals.get('number', _('New')) == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code('inward.material') or _('New')
        else:
            vals['number'] = self.env['ir.sequence'].next_by_code('inward.material') or _('New')
        result = super(InwardMaterial, self).create(vals)
        return result

    @api.multi
    def create_inward_invoice(self,Inward):
        invoice_id = self.env['account.invoice'].create({
            'partner_id': Inward.supplier_id and Inward.supplier_id.id or False,
            'currency_id': self.env.ref('base.INR').id,
            'name': Inward.name + (Inward.short_number or ''),
            'account_id': self.supplier_id.property_account_payable_id and self.supplier_id.property_account_payable_id.id,
            'type': 'in_invoice',
            'date_invoice': datetime.today(),
            'origin': Inward.product_id.name,
        })
        self.env['account.invoice.line'].create({
            'product_id': Inward.product_id and Inward.product_id.id or False,
            'quantity': Inward.quantity or 0.0,
            'price_unit': Inward.rate or 0.0,
            'invoice_id': invoice_id.id,
            'name': Inward.product_id.name,
            'account_id': Inward.product_id.property_account_expense_id.id or Inward.product_id.categ_id.property_account_expense_categ_id.id,
        })
        invoice_id._onchange_invoice_line_ids()
        return invoice_id

    @api.multi
    def action_view_invoice(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        if len(self.invoice_ids) > 1:
            result['domain'] = "[('id', 'in', %s)]" % self.invoice_ids.ids
        else:
            form_view = self.env.ref('account.invoice_form')
            result['views'] = [(form_view.id, 'form')]
            result['res_id'] = self.invoice_ids.id
        return result

    @api.multi
    def action_send_for_approval(self):
        self.state = 'waiting_approval'
        return True
    
    @api.multi
    def action_inward_material(self):
        for Inward in self:
            if Inward.quantity <= 0.0:
                raise UserError(_("Please Enter Quantity more than Zero"))
            ShortNumber = Inward.short_number or ''
            ProductName = Inward.name + ShortNumber + '-' + Inward.number
            RouteID = self.env['stock.location.route'].search([('name','=','Buy')],limit=1)
            ProcurementRuleID = self.env['procurement.rule'].search([('action','=','buy')],limit=1)
            ProductID = self.env['product.product'].create({'name': ProductName,
                                                            #'route_ids': [(4, RouteID.id)],
                                                            'uom_id':Inward.product_uom_id and Inward.product_uom_id.id or False,
                                                            'uom_po_id':Inward.product_uom_id and Inward.product_uom_id.id or False,
                                                            'default_code': Inward.number or '',
                                                            'company_id': False,
                                                            'type':'product'})
            SourceLocation = self.env['stock.location'].search([('company_id','=',self.env.user.company_id.id),('usage','=','supplier'),('name','in',('Vendor','Vendors'))],limit=1)
            StockMoveDict = {
                             'name': ProductName or '/',
                             'location_id': SourceLocation and SourceLocation.id or False,
                             'location_dest_id':Inward.location_id and Inward.location_id.id or False,
                             'product_id': ProductID and ProductID.id or False,
                             'product_uom': Inward.product_uom_id and Inward.product_uom_id.id or False,
                             'product_uom_qty': Inward.quantity or 0.0, 
                             'origin': ProductName or '',
                             'reference': ProductName or '',
                             }
            StockMove = self.env['stock.move'].create(StockMoveDict)
            StockMove._action_confirm()
            StockMove._action_assign()
            StockMove.move_line_ids.write({'qty_done': Inward.quantity})
            StockMove._action_done()
            Inward.state = 'inward'
            Inward.product_id = ProductID and ProductID.id or False
            invoice_id = self.create_inward_invoice(Inward)
            Inward.invoice_ids = [(6, 0, [invoice_id.id])]
        return True

    @api.multi
    def unlink(self):
        ProductionObj = self.env['production.process']
        for inward in self:
            InwardInCutting = ProductionObj.search([('state','!=','design'),('inward_material_id','=',inward.id)])
            if len(InwardInCutting) > 0:
                raise UserError(_('You Can not Delete Material Inward which Material is in Stitching'))
            else:
                DesignId = ProductionObj.search([('inward_material_id','=',inward.id),('state','=','design')])
                DesignId.unlink()
        return super(InwardMaterial, self).unlink()

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})