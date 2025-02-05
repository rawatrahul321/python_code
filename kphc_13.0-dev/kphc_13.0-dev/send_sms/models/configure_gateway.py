from odoo import models, fields, api


class SmsMailServer(models.Model):

    _name = "sms.mail.server"
    _description = "Module for sms mail server configuration."
    _rec_name = 'description'

    @api.model
    def get_reference_type(self):
        return []

    description = fields.Char(string="Description", required=True)
    sequence = fields.Integer(
        string='Priority', help="Default Priority will be 10.", default=10)
    sms_debug = fields.Boolean(
        string="Debugging", help="If enabled, the error message of sms gateway will be written to the log file")
    user_mobile_no = fields.Char(
        string="Mobile No. (To Receive Test SMS)", help="Ten digit mobile number with country code(e.g +91)")
    gateway = fields.Selection('get_reference_type', string="SMS Gateway")
    api_key = fields.Char("API Key")
    sender_id = fields.Char("Sender ID")
    channel = fields.Char("Channel")
    route_id = fields.Char("Route ID")
