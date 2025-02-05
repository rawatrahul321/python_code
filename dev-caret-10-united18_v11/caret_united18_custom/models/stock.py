#  -*- coding: utf-8 -*-
 
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.addons import decimal_precision as dp

class StockLocation(models.Model):
    _inherit = "stock.location"

    def name_get(self):
        ret_list = []
        for location in self:
            orig_location = location
            name = location.name
            if location.location_id and location.usage != 'view':
                if not name:
                    raise UserError(_('You have to set a name for this location.'))
                if location.company_id:
                    name = '['+str(location.company_id.name)+']'+' ' + location.location_id.name + "/" + name
                else:
                    name = location.location_id.name + "/" + name
            ret_list.append((orig_location.id, name))
        return ret_list


class StockPickingLR(models.Model):
    _inherit = 'stock.picking'
    

    lr_number = fields.Char(string="LR Number")
    carrier_info = fields.Text(string="Carrier Info")
    # amount_total = fields.Float(compute='_amount_all', string="Total", store=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,\
        default=lambda self: self.env.user.company_id.currency_id.id)
    
    # @api.depends('move_lines.price_subtotal')
    # def _amount_all(self):
    #     for order in self:
    #         amount_total = 0.0
    #         for line in order.move_lines:
    #             amount_total += line.price_subtotal
    #         order.update({
    #             'amount_total': amount_total,
    #         })



    @api.multi
    def action_view_invoice(self):
        print("action_view_invoice===================")
        ctx = self._context.copy()
        ctx.update({
            'default_picking_id': self.id,
            })
        invoices = self.env['account.invoice'].search([
            ('picking_id', '=', self.id)])
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
        action['context'] = ctx
        return action


    def send_sms_for_picking(self):
        if not self.lr_number or not self.carrier_info or not (self.lr_number and self.carrier_info):
            raise UserError(_('Please set missing value from LR Number or Carrier Info'))
        sms_template = self.env['ir.model.data'].get_object('caret_sms', 'stock_picking_sms_template')
        sms_rendered_content = self.env['sms.body.template'].render_template(sms_template.template_body, sms_template.model, self.id)
        api_key = self.env['ir.config_parameter'].sudo().get_param('caret_sms.textlocal_api_key')
        sender = self.env['ir.config_parameter'].sudo().get_param('caret_sms.sender')
        to_number = ''
        to_mobile = self.partner_id.mobile or self.partner_id.phone
        if to_mobile:
            if len(to_mobile) == 10:
                to_number = str(91) + to_mobile
            elif '+' in to_mobile and len(to_mobile) == 13:
                to_number = to_mobile.replace('+','').strip()
            elif '+' in to_mobile and len(to_mobile) == 11:
                to_number = to_mobile.replace('+','').strip()
            elif '+' in to_mobile and len(to_mobile) == 11:
                to_number = to_mobile.replace('+','').strip()
            SMS_record = self.env['sms.sms'].create({'textlocal_api_key':api_key,
                                        'to_number': to_number,
                                        'message': sms_rendered_content,
                                        'sender': sender,
                                        'res_id': self.id or False,
                                        'res_model': 'stock.picking',
                                        })
            SMS_record.sendSMS()
        return True

        
class StockMove(models.Model):
    _inherit = "stock.move"

    # price_subtotal = fields.Float(compute='_compute_amount', string="Subtotal", store=True)    
    currency_ids = fields.Many2one('res.currency', 'Currency', required=True,\
        default=lambda self: self.env.user.company_id.currency_id.id)

    # @api.depends('product_qty', 'price_unit')
    # def _compute_amount(self):
    #     for line in self:
    #         line.price_subtotal = line.product_qty * line.price_unit

    
#     def send_sms_for_picking(self):
#         if not self.lr_number or not self.carrier_info or not (self.lr_number and self.carrier_info):
#             raise UserError(_('Please set missing value from LR Number or Carrier Info'))
#         sms_template = self.env['ir.model.data'].get_object('caret_sms', 'stock_picking_sms_template')
#         sms_rendered_content = self.env['sms.body.template'].render_template(sms_template.template_body, sms_template.model, self.id)
#         api_key = self.env['ir.config_parameter'].sudo().get_param('caret_sms.textlocal_api_key')
#         sender = self.env['ir.config_parameter'].sudo().get_param('caret_sms.sender')
#         to_number = ''
#         to_mobile = self.partner_id.mobile or self.partner_id.phone
#         if to_mobile:
#             if len(to_mobile) == 10:
#                 to_number = str(91) + to_mobile
#             elif '+' in to_mobile and len(to_mobile) == 13:
#                 to_number = to_mobile.replace('+','').strip()
#             elif '+' in to_mobile and len(to_mobile) == 11:
#                 to_number = to_mobile.replace('+','').strip()
#             elif '+' in to_mobile and len(to_mobile) == 11:
#                 to_number = to_mobile.replace('+','').strip()
#             SMS_record = self.env['sms.sms'].create({'textlocal_api_key':api_key,
#                                         'to_number': to_number,
#                                         'message': sms_rendered_content,
#                                         'sender': sender,
#                                         'res_id': self.id or False,
#                                         'res_model': 'stock.picking',
#                                         })
#             SMS_record.sendSMS()
#         return True

class StockQty(models.Model):
    """ website_product_qty field update """
    _inherit = 'stock.quant'

    @api.multi
    def write(self,vals):
        res = super(StockQty, self).write(vals)
        if vals.get('quantity') and self.location_id.company_id.id == 1:
            product_tmp_id = self.product_id.product_tmpl_id
            product_tmp_id.get_website_product_qty()
        return res

    @api.model
    def create(self,vals):
        res = super(StockQty, self).create(vals)
        if vals.get('quantity') and res.location_id.company_id.id == 1:
            product_tmp_id = res.product_id.product_tmpl_id
            product_tmp_id.get_website_product_qty()
        return res