from odoo import api, fields, models

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.multi
    def write(self, vals):
        a = self.env['pos.order'].search([('id','=',self.id)])
        if a.lines.qty < 0:
            vals['qty'] = -vals.get('qty')
        return super(PosOrderLine, self).write(vals)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    cash = fields.Char(string="Cash", store=True,compute='_compute_amount_all')
    digital = fields.Char(string="Digital", store=True,compute='_compute_amount_all')

    @api.depends('statement_ids', 'lines.price_subtotal_incl', 'lines.discount')
    def _compute_amount_all(self):
        super(PosOrder, self)._compute_amount_all()
        for order in self:
            for lin in order.statement_ids:
                if lin.journal_id.name =='Cash':
                    order.cash = 'Cash'
                if lin.journal_id.name == 'Digital':
                    order.digital = 'Digital'


    @api.model
    def send_order_sms(self,order_id):
        pos_order = self.search([('pos_reference', '=','Order '+ order_id)])
        sms_template = self.env['ir.model.data'].get_object('caret_sms', 'pos_order_sms_template')
        sms_rendered_content = self.env['sms.body.template'].render_template(sms_template.template_body, sms_template.model, pos_order.id)
        api_key = self.env['ir.config_parameter'].sudo().get_param('caret_sms.textlocal_api_key')
        sender = self.env['ir.config_parameter'].sudo().get_param('caret_sms.sender')
        to_mobile = pos_order.partner_id.mobile or pos_order.partner_id.phone
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
                to_number = pos_order.partner_id.mobile
            SMS_record = self.env['sms.sms'].create({'textlocal_api_key':api_key,
                                        'to_number': to_number,
                                        'message': sms_rendered_content,
                                        'sender': sender,
                                        'res_id': pos_order.id or False,
                                        'res_model': 'pos.order',
                                        })
            SMS_record.sendSMS()
