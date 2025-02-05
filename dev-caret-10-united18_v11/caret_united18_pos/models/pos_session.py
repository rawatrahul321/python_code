import datetime
from odoo import api, fields, models, tools, SUPERUSER_ID

DTFORMAT = tools.DEFAULT_SERVER_DATETIME_FORMAT

class PosConfig(models.Model):
    _inherit = 'pos.config'

    cash_control = fields.Boolean(string='Cash Control', help="Check the amount of the cashbox at opening and closing.",
        default=True)

class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.multi
    def posSessionClose(self):
        todaydate = datetime.date.today()
        sessions = self.env['pos.session'].search([('state', '!=', 'closed')],limit=30)
        pos_configs = self.env['pos.config'].search([('cash_control', '=', False)])
        for config in pos_configs:
            config.write({'cash_control': True})
        for session in sessions:
            if session.start_at:
                session_date = datetime.datetime.strptime(session.start_at, DTFORMAT).date()
                if (session_date != todaydate):
                    posOrders = self.env['pos.order'].search([
                        ('state', '=', 'draft'),
                        ('session_id', '=', session.id)
                    ])
                    posOrders.unlink()
                    session.action_pos_session_closing_control()
                    session.action_pos_session_validate()

    @api.model
    def create(self, values):
        config_id = values.get('config_id') or self.env.context.get('default_config_id')
        if not config_id:
            raise UserError(_("You should assign a Point of Sale to your session."))

        # journal_id is not required on the pos_config because it does not
        # exists at the installation. If nothing is configured at the
        # installation we do the minimal configuration. Impossible to do in
        # the .xml files as the CoA is not yet installed.
        pos_config = self.env['pos.config'].browse(config_id)
        ctx = dict(self.env.context, company_id=pos_config.company_id.id)
        uid = SUPERUSER_ID if self.env.user.has_group('point_of_sale.group_pos_user') else self.env.user.id
        for journal in pos_config.journal_ids:
            # set the journal_id which should be used by
            # account.bank.statement to set the opening balance of the
            # newly created bank statement
            ctx['journal_id'] = journal.id if pos_config.cash_control and journal.type == 'cash' else False        
        res = super(PosSession, self.with_context(ctx).sudo(uid)).create(values)
        pos_name = self.env['ir.sequence'].with_context(ctx).next_by_code('pos.session.custom')
        res.name = 'POS/' + (pos_config.company_id.sudo().partner_id.customer_id or '') + '/' + pos_name
        for stmt in res.statement_ids:
            stmt.name = res.name
        return res