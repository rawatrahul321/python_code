# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    channable_order_id = fields.Char('Channable Order')
    channable_commission = fields.Float('Commission')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('channable_order', 'Channable Order'),
        ('sent', 'Quotation Sent'),
        ('review', 'Error Order'),
        ('vendor_process', 'Vendor Process'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')
    is_channable_error_order = fields.Boolean('Is Error Order')
    order_platform_id = fields.Char('Order Platform Id')
    channable_channel_id = fields.Many2one('channable.order.channel', string='MarketPlace')
    marketplace_id = fields.Char('MarketPlace Order ID', related='channable_channel_id.channel_id')
    is_exported_to_ftp = fields.Boolean('is Exported to FTP')
    delivery_validate_error = fields.Text('Auto Delivery Validation Issue')
    channable_order_date = fields.Datetime('Channable Order Date')
    vendor_process_date = fields.Datetime('Vendor Process Date')
    tracking_urls = fields.Char('Tracking URLs', compute='_compute_tracking_urls')
    is_empty_shipping = fields.Boolean('Is Empty Shipping')
    channable_project_id = fields.Char('Channable Project ID')
    is_fbm_order = fields.Boolean('Is FBM Order')

    def _compute_tracking_urls(self):
        for rec in self:
            urls = []
            for picking in rec.picking_ids:
                if picking.tracking_url:
                    urls.append(picking.tracking_url)
            if urls:
                rec.tracking_urls = ", ".join(urls)

    @api.multi
    def write(self, values):
        if 'order_line' in values:
            lines = [line[1] for line in values['order_line'] if type(line[1]) == int and line[0] == 2]
            if lines:
                orderLines = self.env['sale.order.line'].browse(lines)
                line = [line.id for line in orderLines if line.product_id.is_review_product]
                if line:
                    self.is_channable_error_order = False
                    # self.write({'state': 'draft', 'is_channable_error_order': False})
        result = super(SaleOrder, self).write(values)
        return result

    @api.multi
    def action_cancel(self):
        if self.channable_order_id:
            conn = self.env['channable.connection'].search([('api_project_id', '=', self.channable_project_id)])
            channableApi = conn.apiConnection()
            cancel_order = channableApi.update_order_cancellation(self.channable_order_id)
            if (cancel_order.get('status') == 'success' or
                (cancel_order.get('status') == 'warning' and 'shipped' in cancel_order.get('message'))):
                return self.write({'state': 'cancel'})
            else:
                raise ValidationError(_(cancel_order.get('message')))
        else:
            return super(SaleOrder, self).action_cancel()

    @api.multi
    def action_channable_order(self):
        for rec in self:
            rec.write({'state': 'channable_order'})

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.marketplace_id:
            res['marketplace_id'] = self.marketplace_id
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    channable_product_commission = fields.Float('Product Commission')
    is_line_review_product = fields.Boolean('is error product', related='product_id.is_review_product')

    @api.model
    def create(self, vals):
        if 'product_id' in vals and 'order_id' in vals:
            product = self.env['product.product'].browse(vals['product_id'])
            if product.is_review_product:
                order = self.env['sale.order'].browse(vals['order_id'])
                order.write({'state': 'review', 'is_channable_error_order': True})
        result = super(SaleOrderLine, self).create(vals)
        return result


class ChannableOrderChannel(models.Model):
    _name = 'channable.order.channel'
    _description = "channable Order Channel"

    name = fields.Char('MarketPlace Name')
    channel_id = fields.Char('MarketPlace Id')
    channel_image = fields.Binary('MarketPlace Logo', attachment=True)
    description = fields.Text('Description')

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = rec.description
            res.append((rec.id, name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        domain = args or []
        domain += [
            '|',
            ('name', operator, name),
            ('description', operator, name),
        ]
        return self.search(domain, limit=limit).name_get()


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _notify_get_reply_to(self, default=None, records=None, company=None, doc_names=None):
        default_template = self._context.get('default_template_id')
        if default_template:
            template = self.env['mail.template'].browse(default_template)
            if template.reply_to:
                default = template.reply_to
        return super(PurchaseOrder, self)._notify_get_reply_to(default=default, records=None, company=company, doc_names=doc_names)
