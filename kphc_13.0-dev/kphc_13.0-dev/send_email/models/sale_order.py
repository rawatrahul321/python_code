# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import api, fields, models
from odoo import http


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # delivery_method = fields.Selection([('express_delivery', 'Express Delivery'), ('standard_delivery' , 'Standard Delivery')], string="Delivery Method")
    amount_delivery = fields.Monetary(
        compute='_compute_amount_delivery',
        string='Delivery Amount',
        help="The amount without tax.", store=True, tracking=True)

    @api.depends('order_line.price_unit', 'order_line.tax_id', 'order_line.discount', 'order_line.product_uom_qty')
    def _compute_amount_delivery(self):
        for order in self:
            if self.env.user.has_group('account.group_show_line_subtotals_tax_excluded'):
                order.amount_delivery = sum(order.order_line.mapped('price_subtotal'))
            else:
                order.amount_delivery = sum(order.order_line.mapped('price_total'))

    # def _find_mail_template(self, force_confirmation_template=False):
    #     template_id = False

    #     if force_confirmation_template or (self.state == 'sale' and not self.env.context.get('proforma', False)):
    #         template_id = int(self.env['ir.config_parameter'].sudo().get_param('sale.default_confirmation_template'))
    #         template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
    #         if not template_id:
    #             template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.mail_template_sale_confirmation', raise_if_not_found=False)
    #     if not template_id:
    #         template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.email_template_edi_sale', raise_if_not_found=False)

    #     return template_id

    # def action_confirm(self):
    #     ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
    #     self.ensure_one()
    #     template_id = self._find_mail_template()
    #     lang = self.env.context.get('lang')
    #     template = self.env['mail.template'].browse(template_id)
    #     self.write({
    #         'state': 'sale'
    #     })
    #     if template.lang:
    #         lang = template._render_template(template.lang, 'sale.order', self.ids[0])
    #     ctx = {
    #         'default_model': 'sale.order',
    #         'default_res_id': self.ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         'mark_so_as_sent': True,
    #         'custom_layout': "mail.mail_notification_paynow",
    #         'proforma': self.env.context.get('proforma', False),
    #         'force_email': True,
    #         'model_description': self.with_context(lang=lang).type_name,
    #     }
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(False, 'form')],
    #         'view_id': False,
    #         'target': 'new',
    #         'context': ctx,
    #     }


    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #     template = self.env.ref('send_email.sale_order_email_template', raise_if_not_found=False)
    #     if template:
    #         template['email_to'] = self.partner_id.email or ''
    #         template.send_mail(self.id)

    #     return res


    def get_url_sale_order(self):
        ''' This function give current record url in email template. '''
        action_ref = self.env.ref('sale.action_orders', False)
        # portal_link = "%s/?db=%s#id=%s&action=%s&view_type=form" % (
        portal_link = "%s/web#id=%s&action=%s&model=sale.order&view_type=form" % (
            self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
            # self.env.cr.dbname,
            self.id,
            action_ref and action_ref.id or False)
        return portal_link
