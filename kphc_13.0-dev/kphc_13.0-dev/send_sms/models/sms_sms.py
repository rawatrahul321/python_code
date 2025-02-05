from odoo import SUPERUSER_ID, api
import re
import operator
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class SmsBase(models.AbstractModel):
    _name = "sms.base.abstract"
    _description = "Contains the logic shared between models which allows to send sms."

    @api.depends("sms_gateway_config_id")
    def get_sms_gateway_name(self):
        for rec in self:
            rec.sms_gateway = rec.sms_gateway_config_id.gateway if rec.sms_gateway_config_id else ""

    @api.model
    def _get_default_config_sms_gateway(self):
        return self.env["sms.mail.server"].search([], order='sequence asc', limit=1)

    to = fields.Char("To:", required=True)
    by = fields.Char("From:")
    msg = fields.Text("Message:", required=True)
    sms_gateway_config_id = fields.Many2one(
        'sms.mail.server', string="SMS Gateway", default=_get_default_config_sms_gateway)
    sms_gateway = fields.Char(
        compute='get_sms_gateway_name', string="Gateway Name")

    
    def send_sms_via_gateway(self, body_sms, mob_no, from_mob=None, sms_gateway=None):
        gateway_obj = sms_gateway if sms_gateway else self.env[
            "sms.mail.server"].search([], order='sequence asc', limit=1)
        if gateway_obj and not gateway_obj.gateway:
            raise Warning("SMS configuration has no gateway.")
        elif gateway_obj and gateway_obj.gateway:
            return gateway_obj
        else:
            _logger.info(
                "***************** No SMS Gateway Configuration  *******************")
            return False

    
    def send_now(self):
        signature = self.env['res.users'].sudo().browse(self._uid).signature
        for obj in self:
            body = obj.msg + '\n' + signature
            body_sms = re.sub("<.*?>", " ", body)
            mob_no = [obj.to]
            obj.with_context(action='send').send_sms_via_gateway(
                body_sms, mob_no, from_mob=None, sms_gateway=obj.sms_gateway_config_id)


class SmsSms(models.Model):
    """SMS sending using SMS mail server."""

    _name = "wk.sms.sms"
    _inherit = 'sms.base.abstract'
    _description = "Model for Sms."
    _rec_name = "group_type"
    _order = "id desc"


    name = fields.Char(string="Title")
    state = fields.Selection([
        ('new', 'Draft'),
        ('sent', 'Sent'),
        ('error', 'Error'),
    ], "State", default='new')
    # auto_delete = fields.Boolean(
    #     "Auto Delete", help="Permanently delete all SMS after sending,to save space.", default=True)
    group_type = fields.Selection([('multiple', 'Multiple Members'),
                                   ('individual', 'Individual Member/Number')], string="SMS To", help="This field is used to send the message for a single customer or group of customer.")
    partner_id = fields.Many2one("res.partner", string="Recipient")
    partner_ids = fields.Many2many(
        "res.partner", "sms_partner_relation", 'sms_id', 'receiver_id', string="Recipients")

    template_id = fields.Many2one(
        'wk.sms.template', string="Template")
