# -*- coding: utf-8 -*-

import odoo.addons.decimal_precision as dp
from decimal import *
getcontext().prec = 2
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import AccessError, UserError, ValidationError


class ReturnOrder(models.Model):
    _name = 'return.order'
    _inherit = 'purchase.order'
    _order = 'product_id DESC'


    location_id = fields.Many2one('stock.location')


    order_id = fields.Many2one('purchase.order','Orders')

    order_line = fields.One2many('return.order.line', 'order_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    scan_line = fields.One2many('return.scan.line', 'return_order_id')
    scan = fields.Char(string="Scan")
    picking_type_id = fields.Many2one(default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Draft Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Return Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    invoice_id = fields.Many2one("account.move", string='Invoices',readonly=True, copy=False)
    discount_account = fields.Many2one('account.account', 'Discount Account')

    apply_discount = fields.Boolean('Apply Discount')
    discount_type_id = fields.Many2one('discount.type', 'Discount Type')
    discount_value = fields.Float('Purchase Discount', digits=dp.get_precision('Discount'))
    now = fields.datetime.now()
    fix_amount_untaxed = fields.Float()
    fixed_amount_total = fields.Float(string="",  readonly=True, )


    def all_create_bonus_line(self):
        for record in self.order_line:
            if record.bonus:
                record.create_bonus_line()

    @api.model
    @api.onchange('order_line')
    def get_discount(self):
        disc=0
        lin_disc=0
        fix =0.0
        total=0
        for line in self.order_line:
            quantity = line.product_qty or 1.0
            price = line.price_unit * quantity
            total +=price
        for line in self.order_line:
                    quantity = line.product_qty or 1.0
                    price = line.price_unit * quantity
                    if line.discount_type == "fixed":

                        if  line.discount_type in ["percent", "bonus"]:
                            continue
                            line.price_subtotal = price
                            if line.discount:
                                disc = total/line.discount
                            if disc:
                                lin_disc= line.price_subtotal/disc
                                price = price - lin_disc
                            line.discount = lin_disc

                            if line.price_subtotal:
                                line.update({
                                             'discount': lin_disc,
                                             'fixed_amount': lin_disc,
                                             'price_subtotal': price,
                                             })
                            fix += line.fixed_amount
                        line.price_avg = line.price_subtotal / line.product_qty
                    elif line.discount_type == "percent":
                        if  line.discount_type in ["fixed", "bonus"]:
                            continue
                        if line.price_avg and line.price_avg != line.price_unit:
                            continue

                        else:
                            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                            quantity = line.product_qty
                            taxes = line.taxes_id.compute_all(
                                price, line.order_id.currency_id, quantity, product=line.product_id, partner=line.order_id.partner_id)
                            line.update({
                                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                                'price_total': taxes['total_included'],
                                'price_subtotal': taxes['total_excluded'],
                                'total': line.price_unit*line.product_qty
                            })
                        line.price_avg = line.price_subtotal / line.product_qty
        self.fix_amount_untaxed = fix
        self.fixed_amount_total = total - self.fix_amount_untaxed
        self.amount_untaxed = total - self.fix_amount_untaxed
        self.amount_total = self.amount_untaxed + self.amount_tax



    @api.onchange('order_line')
    def create_bonus_line(self):
        for record in self.order_line:
            print("uuuuuuuuuuuuuuuuuuuu")
            if record.bonus and record.discount_type == "bonus":
                if record.price_unit == 0.0:
                    raise ValidationError(_('Must Be Unit Price Of Products More Than 0 '))
                if self.order_line:
                    for line in self.order_line:
                        if line.bonus :
                            pr = ((line.product_qty * line.discount) - (line.product_qty)) - int(
                                (line.product_qty * line.discount) - (line.product_qty))
                            print("pr", pr)
                            if pr:
                                if line.bonus and line.discount_type == "bonus":
                                    if line.discount:
                                        line.discount_type = "fixed"
                                        line.price_avg = line.price_subtotal / line.product_qty
                                        line.bonus  = False
                                        # line.name  =line.name + "/ + Bonus"
                else:
                    raise ValidationError(_('Order Lines Not Found. '))

    def all_create_bonus_line(self):
        for record in self.order_line:
            if record.bonus:
                record.create_bonus_line()


    def _percent_discount(self):
        qty = 0.0
        p_unit = 0.0
        dis = 0
        for line in self.order_line:
            for rec in self.order_line:
                if rec.bonus and rec.product_id.id == line.product_id.id:
                    if rec.discount_type ==  "percent":
                        rec.discount = 100
                    qty += rec.product_qty
                    p_unit += rec.price_subtotal
                    dis += rec.discount
                rec.price_avg = (p_unit / qty) / dis
            line.bonus = False


    @api.onchange('amount_untaxed','order_line')
    def _onchange_amount_total(self):
        if self.amount_untaxed and not self.amount_tax :
            self.amount_total = self.amount_untaxed
        if self.amount_untaxed and  self.amount_tax :
            self.amount_total = self.amount_untaxed + self.amount_tax



    @api.onchange('partner_id')
    def onchange_order_id(self):
        for rec in self:
            return {'domain': {'order_id': [('partner_id', '=', rec.partner_id.id)]}}







    @api.model
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'outgoing'), ('warehouse_id', '=', False)])
        return types[:1]


    def action_view_invoi(self):
        for rec in self:
            journal = self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', self.company_id.id)], limit = 1)
            invoice_line_vals=[]
            inv_obj = self.env['account.move']
            for order in self.order_line:
                if "Bonus" in order.name:
                    invoice_line_vals.append((0,0,{
                        'account_id':order.product_id.categ_id.property_stock_account_output_categ_id.id,
                        'name':  order.product_id.name +'/' + 'Bonus',
                        'product_id': order.product_id.id,
                        'product_uom_id': order.product_uom.id,
                        'quantity': order.product_qty,
                        'price_unit': order.price_unit,
                        'discount_type': order.discount_type,
                        'discount': order.discount,
                        'price_subtotal': order.price_subtotal,
                        'tax_ids': [(6, 0, order.taxes_id.ids)],
                        'analytic_account_id': order.account_analytic_id.id,
                        'analytic_tag_ids': [(6, 0, order.analytic_tag_ids.ids)],
                        'return_line_id': order.id,
                        'exclude_from_invoice_tab': False,
                    }))
                else:
                    invoice_line_vals.append((0,0,{
                        'account_id':order.product_id.categ_id.property_stock_account_output_categ_id.id,
                        'name':  order.product_id.name ,
                        'product_id': order.product_id.id,
                        'product_uom_id': order.product_uom.id,
                        'quantity': order.product_qty,
                        'price_unit': order.price_unit,
                        'discount_type': order.discount_type,
                        'discount': order.discount,
                        'price_subtotal': order.price_subtotal,
                        'tax_ids': [(6, 0, order.taxes_id.ids)],
                        'analytic_account_id': order.account_analytic_id.id,
                        'analytic_tag_ids': [(6, 0, order.analytic_tag_ids.ids)],
                        'return_line_id': order.id,
                        'exclude_from_invoice_tab': False,
                    }))
            inv_data = {
                'type': 'in_refund',
                'name': rec.name,
                'pr_return': rec.id,
                'return_id': rec.id,
                'apply_discount': True,
                'ref': rec.name,
                'currency_id': rec.partner_id.property_product_pricelist.currency_id.id,
                'journal_id': journal.id or 1,
                'invoice_origin': rec.name,
                'company_id': rec.company_id.id,
                'partner_id': rec.partner_id.id,
                'invoice_line_ids': invoice_line_vals,

            }
            inv_id = inv_obj.create(inv_data)
            # inv_id.action_post()

            return inv_id















    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('return.order') or '/'
        return super(ReturnOrder, self).create(vals)

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        for rec in self:
            rec.dest_address_id = rec.picking_type_id.default_location_src_id.id


    def add_products(self):
        line_list = []
        flag = 0

        for s in self.scan_line:
            product_obj = s.product_id
            qty = s.product_qty

            # TODO check for existing records too
            for record in self.order_line:
                if record.product_id.id == product_obj.id:
                    record.product_qty += qty
                    flag = 1
                line_list.append((4, record.id))

            if not flag:
                vals = {
                    'order_id': self.id,
                    'product_id': product_obj.id,
                    'name': product_obj.name,
                    'product_qty': qty,
                    'discount': s.discount,
                    'price_unit': product_obj.product_tmpl_id.list_price,
                    'product_uom': product_obj.product_tmpl_id.uom_id.id,
                    'state': 'draft',
                    'date_planned': fields.Date.today()
                }
                res = self.order_line.create(vals)
            s.unlink()

    @api.model
    def _prepare_picking(self):

        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self.partner_id.property_stock_supplier.id,
            'return_id': self.id,
            'location_id':  self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }


    def open_invoice(self):
        return {
            'name': _('INVOICES'),
            'domain': [('name', '=', self.name)],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': "tree,form",
            'type': 'ir.actions.act_window',
        }
    def open_pick(self):
        return {
            'name': _('Transfer'),
            'domain': [('origin', '=', self.name)],
            'view_type': 'form',
            'res_model': 'stock.picking',
            'view_id': False,
            'view_mode': "tree,form",
            'type': 'ir.actions.act_window',
        }

    course_count = fields.Integer(string="Counter", required=False, compute='_compute_counter')
    picking_co = fields.Integer(string="Counter", required=False, compute='_compute_counter_pick')

    def _compute_counter(self):
        res = self.env['account.move'].search([('name', '=', self.name)])
        if res:
            self.course_count = len(res)
        else:
            self.course_count = 0
        pass
    def _compute_counter_pick(self):
        res = self.env['stock.picking'].search([('origin', '=', self.name)])
        print(res)
        if res:
            self.picking_co = len(res)
            print(len(res))
        else:
            self.picking_co = 0
        pass


class ReturnOrderLine(models.Model):
    _name = 'return.order.line'
    _inherit = 'purchase.order.line'
    _order = 'id asc'

    bonus = fields.Boolean()
    price_reduce = fields.Monetary(compute='_get_price_reduce', string='Price Reduce', readonly=True)
    discount = fields.Float(string='Discount', digits=dp.get_precision('Discount'), default=0.0)
    discount_type = fields.Selection([
        ('fixed', 'Amount'),
        ('bonus', 'Bonus'),
        ('percent', 'Percent')
    ], string="Discount Type", )

    total = fields.Float('Total Purchase Line',  )
    fixed_amount = fields.Float(string="",  required=False, )
    subtotal_fixed_dis = fields.Float(string="",  required=False, )
    original_price = fields.Float()
    now = fields.datetime.now()
    cal_bonus = fields.Integer( compute= "cal_bonus")
    price_avg = fields.Float(digits=dp.get_precision('Discount'))
    # price_unit = fields.Float(digits=dp.get_precision('Discount'))




    order_id = fields.Many2one('return.order', string='Order Reference', index=True, required=True, ondelete='cascade')
    move_ids = fields.One2many('stock.move', 'return_line_id', string='Reservation',
                               readonly=True, ondelete='set null', copy=False)
    invoice_lines = fields.One2many('account.move.line', 'return_line_id',
                                    string="Bill Lines", readonly=True, copy=False)
    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount', 'discount_type')
    def _compute_amount(self):

        for line in self:

            quantity = line.product_qty or 1.0
            new_price = line.price_unit * quantity
            line.price_subtotal = new_price
            price = line.price_unit * quantity
            if line.discount:
                if line.discount_type == 'fixed':
                    new_price = new_price - line.discount
                elif line.discount_type == 'percent':
                    new_price = new_price - (line.discount*new_price/100.0)
                elif line.discount_type == 'bonus':
                    new_price = new_price

            taxes = line.taxes_id.compute_all(
                price, line.order_id.currency_id, quantity, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': new_price,
                'total': price - new_price
            })



    @api.onchange('product_id', 'discount_type')
    def bonus_flag(self):
        if self.discount_type == 'bonus'  :
            self.bonus = True
        if self.discount_type != 'bonus' :
            self.bonus = False

    def create_bonus_line(self):
        for record in self:
            print("uuuuuuullllllluuuuuuuuuuuuu")
            if record.bonus and record.discount_type == "bonus":
                if record.price_unit == 0.0:
                    raise ValidationError(_('Must Be Unit Price Of Products More Than 0 '))
                if not record.discount :
                    raise ValidationError(_('Must Be discount More Than 0 '))
                qty = 0.0
                p_unit = 0.0
                dis = 0

                for line in self:
                    if line.bonus :
                        pr = ((line.product_qty * line.discount) - (line.product_qty)) - int(
                            (line.product_qty * line.discount) - (line.product_qty))
                        print("pr", pr)
                        for rec in self:
                            if rec.bonus and rec.product_id.id == line.product_id.id:
                                if rec.discount_type == "percent":
                                    rec.discount = 100
                                qty += rec.product_uom_qty
                                p_unit += rec.price_subtotal
                                dis += rec.discount
                            rec.price_avg = (p_unit / qty) / dis
                        val = {
                                'product_id': line.product_id.id,
                                'name': (str(line.name ) + ' ' + '/' + 'Bonus'),
                                'date_planned': self.now,
                                'product_qty': int(
                                    (line.product_qty * line.discount) - (line.product_qty)),
                                'bonus': True,
                                'product_uom': line.product_uom.id,
                                'price_unit': line.price_unit,
                                'price_avg': line.price_avg,
                                'discount_type': "percent",
                                'discount': 100,
                                # 'Taxes_id': line.Taxes_id.ids,
                                'price_subtotal': 0.0,
                                'order_id': line.order_id.id,
                        }
                        line.create(val)
                        self._percent_discount()

    def _percent_discount(self):
        qty = 0.0
        p_unit = 0.0
        dis = 0
        for line in self:
            for rec in self:
                if rec.bonus and rec.product_id.id == line.product_id.id:
                    if rec.discount_type ==  "percent":
                        rec.discount = 100
                    qty += rec.product_qty
                    p_unit += rec.price_subtotal
                    dis += rec.discount
                rec.price_avg = (p_unit / qty) / dis
            line.bonus = False





    def _onchange_quantity(self):
        res = super(ReturnOrderLine, self)._onchange_quantity()
        if self.order_id.order_id:
            for record in self.order_id.order_id.order_line:
                for rec in self:
                    if rec.product_id.id == record.product_id.id:
                        rec.price_unit = record.price_unit
        return res




    @api.onchange('product_id')
    def onchange_order_id(self):
        for rec in self:
            if self.order_id.order_id:
                x = []
                for o_l  in self.order_id.order_id.order_line:
                    for l in o_l.product_id:
                        x.append(l.id)
                return {'domain': {'product_id': [('id', '=', x), ]}}






    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()

        for line in self:

            if line.product_id.type not in ['product', 'consu']:
                continue
            qty = 0.0
            price_unit = line._get_stock_move_price_unit()
            product = line.product_id.with_context(lang=line.order_id.dest_address_id.lang or self.env.user.lang)
            description_picking = product._get_description(line.order_id.picking_type_id)
            # if line.product_description_variants:
            #     description_picking += line.product_description_variants
            date_planned = line.date_planned or line.order_id.date_planned

            for move in line.move_ids.filtered(lambda x: x.state != 'cancel'):
                qty += move.product_qty
            template = {
                'name': (line.name or '')[:2000],
                'product_id': line.product_id.id,
                'date': date_planned,
                # 'date_deadline': date_planned + relativedelta(days=line.order_id.company_id.po_lead),
                'location_id': line.order_id.partner_id.property_stock_supplier.id,
                'location_dest_id': (line.orderpoint_id and not (
                            line.move_ids | line.move_dest_ids)) and line.orderpoint_id.location_id.id or line.order_id._get_destination_location(),
                'picking_id': picking.id,
                'partner_id': line.order_id.dest_address_id.id,
                'move_dest_ids': [(4, x) for x in line.move_dest_ids.ids],
                'state': 'draft',
                'return_line_id': line.id,
                'company_id': line.order_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': line.order_id.picking_type_id.id,
                'group_id': line.order_id.group_id.id,
                'origin': line.order_id.name,
                'description_picking': description_picking,
                'propagate_cancel': line.propagate_cancel,
                'route_ids': line.order_id.picking_type_id.warehouse_id and [
                    (6, 0, [x.id for x in line.order_id.picking_type_id.warehouse_id.route_ids])] or [],
                'warehouse_id': line.order_id.picking_type_id.warehouse_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
            }
            # Fulfill all related procurements with this po line
            diff_quantity = line.product_qty - qty

            if float_compare(diff_quantity, 0.0, precision_rounding=line.product_uom.rounding) > 0:
                template['product_uom_qty'] = diff_quantity
                done += moves.create(template)

        return done





# clearing out default picking type in PO
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    picking_type_id = fields.Many2one(default=False)


class AccountInvoice(models.Model):
    _inherit = 'account.move'


    pr_return = fields.Many2one('return.order')


    # _sql_constraints = [
    # ('number_uniq', 'Check(1=1)', 'Invoice Number must be unique per Company!'),
    # ]



class ReturnScanLine(models.Model):
    _name = 'return.scan.line'

    product_id = fields.Many2one('product.product')
    product_qty = fields.Float(string="Quantity")
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'))

    # inverse field
    return_order_id = fields.Many2one('return.order')


