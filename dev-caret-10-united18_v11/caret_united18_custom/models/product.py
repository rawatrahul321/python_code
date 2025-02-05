# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'


    pos_count = fields.Integer(compute='_pos_count', string='# Pos')

    @api.multi
    def _pos_count(self):
        domain = [
            ('product_id', 'in', self.mapped('id')),
             ('company_id', '=', self.env.user.company_id.id)]
        Pos = self.env['pos.order.line'].search(domain)
        for product in self:
            product.pos_count = len(Pos.filtered(lambda r: r.product_id == product).mapped('order_id'))

class ProductTemplate(models.Model):
    """ display number of point of sales and set default company false on creation of product 
        final sale price field add and assign category in pos and website on onchange of product category """

    _inherit = "product.template"

    final_sales_price = fields.Float('End User Price')
    available_size = fields.Char('Available Size')
    colours = fields.Integer('Colours')
    pcs = fields.Integer('PCS')
    website_product_qty = fields.Float(compute='website_product_quantity',string='Website Product Available',store=True)
    website_product_qty_restrict = fields.Boolean(string='Website Product Qty Restrict')
    restrict_time = fields.Integer('Restrict Hours')
    restrict_qty = fields.Integer('Restrict Quantity')
    restrict_date_start = fields.Datetime(string='Restrict From')



    @api.multi
    def get_website_product_qty(self):
        # my code( available quantity show on website and product unpublished if qty less then 1)
        user_id = self.env['ir.config_parameter'].sudo().get_param('caret_united18_website.user_id_for_available_stock', default=1)
        if user_id != 'False':
            SaleLine = self.env['sale.order.line']

            for product in self:
                qtyOnHand = product.sudo(user_id).qty_available
                available_qty = qtyOnHand - sum([
                    x['product_uom_qty'] - x['qty_delivered']
                        for x in SaleLine.sudo().search_read(
                            [('product_id', 'in', product.product_variant_ids.ids), ('state', 'in', ['sent','sale'])], fields=['product_uom_qty','qty_delivered'])
                ])
                if product.website_product_qty != available_qty:
                    product.website_product_qty = available_qty
                if available_qty < 1 and product.website_published:
                    product.website_published = False
        return True

    @api.depends('qty_available')
    def website_product_quantity(self):
        self.get_website_product_qty()

    def website_publish(self):
        self.website_published = True
        return True

    def website_unpublish(self):
        self.website_published = False
        return True

    @api.multi
    def change_so_lines_price(self):
        sol_ids = self.env['sale.order.line'].search(
            [('state', 'not in', ['done','sale']),
            ('product_id', 'in', self.product_variant_ids.ids)])
        for sol in sol_ids:
            sol.price_unit = self.list_price


    @api.multi
    def _purchase_count(self):
        for template in self:
            template.pos_count = sum([p.pos_count for p in template.product_variant_ids])
        return True

    @api.multi
    def _picking_sales_count(self):
        r = {}
        domain = [
            ('state', 'in', ['draft', 'sent']),
            ('order_id.is_picking', '=', True),
            ('product_id', 'in', self.product_variant_ids.ids),
        ]
        sol = self.env['sale.order.line'].search(domain)
        print("sol======================",sol)
        self.picking_sales_count = sum([sl.product_uom_qty for sl in sol.filtered(lambda r: r.product_id.id in self.product_variant_ids.ids)])
        print("self.picking_sales_count============",self.picking_sales_count)

    pos_count = fields.Integer(compute='_pos_count', string='# POS')
    picking_sales_count = fields.Integer(compute='_picking_sales_count', string='# Picking SO')

    @api.multi
    def action_view_pos(self):
        self.ensure_one()
        action = self.env.ref('point_of_sale.action_pos_order_line')
        product_ids = self.with_context(active_test=False).product_variant_ids.ids

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': "{'default_product_id': " + str(product_ids[0]) + "}",
            'res_model': action.res_model,
            'domain': [('product_id.product_tmpl_id', '=', self.id),
                       ('company_id', '=', self.env.user.company_id.id)],
        }

    @api.multi
    def action_view_picking_sales(self):
        self.ensure_one()
        action = self.env.ref('sale.action_product_sale_list')
        product_ids = self.with_context(active_test=False).product_variant_ids.ids

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': "{'default_product_id': " + str(product_ids[0]) + "}",
            'res_model': action.res_model,
            'domain': [('state', 'in', ['draft', 'sent']),
                       ('order_id.is_picking', '=', True),
                       ('product_id.product_tmpl_id', '=', self.id)],
        }


    @api.model
    def create(self,vals):
        if vals.get('website_published') and vals.get('website_product_qty_restrict'):
            vals['restrict_date_start'] = fields.Datetime.now()
        res = super(ProductTemplate,self).create(vals)

        pos_category = self.env['pos.category']
        website_category = self.env['product.public.category']

        pos_categ_id = pos_category.search([('name','=',res.categ_id.name)],limit=1)
        website_categ_id = website_category.search([('name','=',res.categ_id.name)],limit=1)

        res.company_id = False
        res.pos_categ_id = pos_categ_id.id or False
        res.public_categ_ids = website_categ_id or False

        if 'inventory_availability' in vals.keys():
            res.inventory_availability = 'always'

        return res

    @api.multi
    def write(self,vals):
        if vals.get('website_published') and vals.get('website_product_qty_restrict'):
            vals['restrict_date_start'] = fields.Datetime.now()
        elif vals.get('website_published') and self.website_product_qty_restrict:
            vals['restrict_date_start'] = fields.Datetime.now()
        elif self.website_published and vals.get('website_product_qty_restrict'):
            vals['restrict_date_start'] = fields.Datetime.now()
        res = super(ProductTemplate,self).write(vals)
        if 'categ_id' in vals.keys():
            pos_category = self.env['pos.category']
            website_category = self.env['product.public.category']

            pos_categ_id = pos_category.search([('name','=',self.categ_id.name)],limit=1)
            website_categ_id = website_category.search([('name','=',self.categ_id.name)],limit=1)

            self.pos_categ_id = pos_categ_id.id or False
            self.public_categ_ids = website_categ_id or False
        return res

class PosCategory(models.Model):
    """ pos and website category created when product category created ,
        also updated and delete together."""

    _inherit = "pos.category"

    parent_id = fields.Many2one('pos.category', string='Parent Category', index=True, ondelete='cascade')


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    parent_id = fields.Many2one('product.public.category', string='Parent Category', index=True, ondelete='cascade')

class ProductCategory(models.Model):
    """ pos and website category created when product category created ,
        also updated and delete together."""

    _inherit = "product.category"

    sale_order_count = fields.Integer(string="Sale Orders",compute='_compute_sale_order_count')

    def _compute_sale_order_count(self):
        for record in self:
            sale_order = record.fetch_sale_order_of_category()
            record.sale_order_count = len(sale_order)
    @api.multi
    def show_sale_orders(self):
        sale_list = []
        sale_ids = self.fetch_sale_order_of_category()
        for sale_id in sale_ids:
            for s_id in sale_id:
                sale_list.append(s_id)
        print("len of sale order===>",len(sale_ids))
        action = self.env.ref('sale.action_quotations').read()[0]
        action['domain'] = [('id','in',sale_list)]
        print("action================>",action)
        return action

    def getChildren(self):
        return self.search([('parent_id', 'child_of', self.ids)])

    def fetch_sale_order_of_category(self):
        self.env.cr.execute("""
            SELECT DISTINCT(so.id)
            FROM sale_order AS so
                LEFT JOIN sale_order_line sol ON so.id = sol.order_id
                LEFT JOIN product_product pr ON sol.product_id = pr.id
                LEFT JOIN product_template pt ON pr.product_tmpl_id = pt.id
                LEFT JOIN product_category pc ON pt.categ_id = pc.id
                WHERE pt.categ_id in (%s)
        """ % (','.join([str(x) for x in self.getChildren().ids])))
        return self.env.cr.fetchall()


    @api.model
    def create(self,vals):
        res = super(ProductCategory,self).create(vals)
        check_exists = self.search(['&',('name','=',res.name),
                                    ('parent_id','=',res.parent_id.id)])
        if len(check_exists.ids) > 1:
            raise UserError(_('this name already exists,Please use other name'))

        pos_category = self.env['pos.category']
        website_category = self.env['product.public.category']

        website_parent_id = False
        pos_parent_id = False
        if vals.get('parent_id'):
            website_parent_id = website_category.search([('name','=',res.parent_id.name)], limit=1).id
            pos_parent_id = pos_category.search([('name','=',res.parent_id.name)], limit=1).id

        pos_category.create({
                            'name':vals['name'] or False,
                            'parent_id': pos_parent_id ,
            })
        website_category.create({
                            'name':vals['name'] or False,
                            'parent_id': website_parent_id,
            })
        return res

    @api.multi
    def write(self,vals):

        check_exists = self.search([('name','=',vals.get('name') or self.name),
                                    ('parent_id','=',vals.get('parent_id') or self.parent_id.id)])
        if check_exists:
            raise UserError(_('this name already exists,Please use other name'))

        pos_category = self.env['pos.category']
        website_category = self.env['product.public.category']
        pos_category_name = pos_category.search([('name','=',self.name)],limit=1)
        website_category_name = website_category.search([('name','=',self.name)],limit=1)
        parent_cat_id = self.search([('id','=',vals.get('parent_id'))])

        for nameds in pos_category_name:
            if vals.get('name'):
                pos_category_name.name = vals.get('name')
                website_category_name.name = vals.get('name')
            if 'parent_id' in vals.keys():
                pos_parent_id = pos_category.search([('name','=',parent_cat_id.name)],limit=1)
                website_parent_id = website_category.search([('name','=',parent_cat_id.name)],limit=1)
                pos_category_name.parent_id = pos_parent_id.id or False
                website_category_name.parent_id = website_parent_id.id or False

        return super(ProductCategory,self).write(vals)

    @api.multi
    def unlink(self):
        pos_category = self.env['pos.category']
        website_category = self.env['product.public.category']
        for obj in self:
            pos_category_name = pos_category.search(['&',('name','=',obj.name),
                                                     ('parent_id','=',obj.parent_id.name)])
            website_category_name = website_category.search(['&',('name','=',obj.name),
                                                             ('parent_id','=',obj.parent_id.name)])
            if pos_category_name:
                pos_category_name.unlink()
            if website_category_name:
                website_category_name.unlink()

        return super(ProductCategory,self).unlink()