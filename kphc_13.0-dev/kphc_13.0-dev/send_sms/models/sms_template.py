from odoo import _, api, fields, models


class SmsTemplate(models.Model):
    "Templates for sending sms"
    _name = "wk.sms.template"
    _description = 'SMS Templates'
    _order = 'name'

    active = fields.Boolean(string="Active", default=True)
    name = fields.Char('Name', required=True)
    auto_delete = fields.Boolean("Auto Delete")
    globally_access = fields.Boolean(
        string="Global", help="if enable then it will consider normal(global) template.You can use it while sending the bulk message. If not enable the you have to select condition on which the template applies.")
    condition = fields.Selection([('order_placed', 'Order Placed'),
                                  ('order_confirm', 'Order Confirmed'),
                                  ('order_delivered', 'Order Delivered'),
                                  ('invoice_vaildate', 'Invoice Validate'),
                                  ('invoice_paid', 'Invoice Paid'),
                                  ('order_cancel', 'Order Cancelled')], string="Conditions", help="Condition on which the template has been applied.")
    model_id = fields.Many2one(
        'ir.model', 'Applies to', compute="onchange_condition", help="The kind of document with this template can be used. Note if not selected then it will consider normal(global) template.", store=True)
    model = fields.Char(related="model_id.model", string='Related Document Model',
                        store=True, readonly=True)
    sms_body_html = fields.Text('Body', translate=True, sanitize=False,
                                help="SMS text. You can also use ${object.partner_id} for dynamic text. Here partner_id is a field of the document(obj/model).")
