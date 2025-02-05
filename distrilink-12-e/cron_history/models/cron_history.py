# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           # 
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

import pytz
from psycopg2.extensions import AsIs

from odoo import models, fields, api, sql_db
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class CronLog(models.Model):
    _name = 'ir.cron.log'
    _description = 'Track cron history Logs'

    name = fields.Char(string='Message')
    log_type = fields.Selection(
        [('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'),
         ('critical', 'Critical')],
        string='Type')
    history_id = fields.Many2one('ir.cron.history')


class CronHistory(models.Model):
    _name = 'ir.cron.history'
    _description = 'Track cron history when enable from ir.cron.'
    _order = 'date desc'

    name = fields.Char(string='Name')
    date = fields.Datetime(string='Date')
    status = fields.Selection(
        [('success', 'Success'), ('fail', 'Failed')],
        string='Status',
        help='It shows whether cron job was successfully executed or not.')
    exception = fields.Text(
        string='Exception',
        help='If cron was failed it shows exeception happened.')
    log_ids = fields.One2many('ir.cron.log', 'history_id')
    cron = fields.Integer()

    @api.model
    def register_exception(self, cron_name, server_action_id, job_id, job_exception):
        """Create history record when cron failed."""
        now = fields.Datetime.now()
        db = sql_db.db_connect(self.env.cr.dbname)

        try:
            cr = db.cursor()

            query = '''INSERT INTO
                "ir_cron_history"
                ("id", "create_uid", "create_date", "write_uid", "write_date", "cron", "date", "exception", "name", "status")
                VALUES
                (nextval(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            params = (
                self._sequence,
                self._uid,
                AsIs("(now() at time zone 'UTC')"),
                self._uid,
                AsIs("(now() at time zone 'UTC')"),
                job_id,
                AsIs("(now() at time zone 'UTC')"),
                "%s" % job_exception, 
                '%s (%s) (Action: %s)' % (cron_name, now, server_action_id),
                'fail'
            )

            cr.execute(query, params)
            cr.commit()
        except psycopg2.OperationalError:
            pass
        finally:
            cr.close()

    # @api.model
    # def register_history(self, cron_name, server_action_id, job_id):
    #     """Create history record when cron successfully runs."""
    #     now = fields.Datetime.now()
    #     return self.create({
    #         'name': '%s (%s) (Action: %s)' % (cron_name, now, server_action_id),
    #         'date': now,
    #         'status': 'success',
    #         'cron': job_id
    #     })

    @api.model
    def register_cron_history(self, cron_name, job_id, messages):
        """Create history record when cron successfully runs."""
        now = fields.Datetime.now()
        timezone = pytz.timezone(self._context.get('tz') or 'Europe/Brussels' or 'UTC')
        history = self.create({
            'name': '%s (%s)' % (cron_name, now.astimezone(timezone).strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
            'date': now,
            'status': 'success',
            'cron': job_id
        })
        for message in messages:
            self.env['ir.cron.log'].create({
                'name': message,
                'log_type': 'info',
                'history_id': history.id
            })
        return history


class IrCron(models.Model):
    _inherit = 'ir.cron'

    track_history = fields.Boolean(
        string='Track History?',
        help='If enabled than create cron execution history.')

    @api.multi
    def toggle_track_history(self):
        """Inverse the value of the field 'track_history' on the records."""
        for record in self:
            record.track_history = not record.track_history

    @api.model
    def _handle_callback_exception(self, cron_name, server_action_id, job_id, job_exception):
        """Support from standard when cron exception this method called.
        We capture exception and make transparent to user.
        """
        res = super(IrCron, self)._handle_callback_exception(cron_name, server_action_id, job_id, job_exception)
        self.env['ir.cron.history'].register_exception(cron_name, server_action_id, job_id, job_exception)
        return res

    # @api.model
    # def _callback(self, cron_name, server_action_id, job_id):
    #     """While running the method associated to a given job, we register
    #     history.
    #     """
    #     history = self.env['ir.cron.history'].register_history(
    #         cron_name, server_action_id, job_id)
    #     # ToDo: add log on history
    #     self.env['ir.cron.log'].create({
    #         'name': 'Start',
    #         'log_type': 'info',
    #         'history_id': history.id
    #     })
    #     res = super(IrCron, self)._callback(cron_name, server_action_id, job_id)
    #     print('\n\n\n\n\n\n', self.env.cr.sql_log_count)
    #     self.env['ir.cron.log'].create({
    #         'name': 'End',
    #         'log_type': 'info',
    #         'history_id': history.id
    #     })
    #     # ToDo: add log on history
    #     return res
