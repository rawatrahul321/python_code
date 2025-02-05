# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import pytz

from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class AuditLog(models.Model):
    _name = 'audit.log'
    _description = 'Audit Logs'

    processed_time = fields.Datetime('Date/Time Processed')
    name = fields.Char('Process Name')
    status = fields.Char('Status')
    api_response = fields.Char('Response')
    error_message = fields.Char('Message')

    @api.model
    def put_audit_log(self, process_name, status, response, error_message):
        """Create log record when cron run successfully or failed."""
        now = fields.Datetime.now()
        timezone = pytz.timezone(self._context.get('tz') or 'Europe/Brussels' or 'UTC')
        log = self.create({
            'processed_time': now.astimezone(timezone).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'name': process_name,
            'status': status,
            'api_response': response,
            'error_message': error_message
        })
        return log
