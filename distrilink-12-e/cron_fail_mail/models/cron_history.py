# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           # 
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

import pytz

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class IrCron(models.Model):
    _inherit = 'ir.cron'

    @api.model
    def _handle_callback_exception(self, cron_name, server_action_id, job_id, job_exception):
        """Support from standard when cron exception this method called.
        We capture exception and make transparent to user.
        """
        res = super(IrCron, self)._handle_callback_exception(cron_name, server_action_id, job_id, job_exception)
        now = fields.Datetime.now()
        timezone = pytz.timezone(self._context.get('tz') or 'Europe/Brussels' or 'UTC')
        mail_template = self.env.ref('cron_fail_mail.email_template_ir_cron_fail')
        mail_template.subject = cron_name + ' Failed on ' + now.astimezone(timezone).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        mail_template.body_html = '<div><p>%s</p></div>'%(job_exception)
        mail_template.send_mail(job_id, force_send=True)
        return res
