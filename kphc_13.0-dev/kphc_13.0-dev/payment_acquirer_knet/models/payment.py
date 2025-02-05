from logging import getLogger
from typing import List, Tuple

from werkzeug.urls import url_join, url_decode

from odoo import models, fields, api, _
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools.float_utils import float_repr

from ..controllers.main import CALLBACK_URL
from ..tools.crypto_tools import encrypt_data, decrypt_data

CURRENCY_CODES = {
    "KWD": "414",
}
_logger = getLogger(__name__)


def _amount_repr(amount: float) -> str:
    return float_repr(amount, 2)


def join_parameters(params: List[Tuple]) -> str:
    res = ""
    for param in params:
        res += f"{param[0]}={param[1]}&"

    return res


def _add_tx_to_current_session(tx):
    # TODO: Due to cookie default SameSite policy change in 2020, Odoo loses session id, and forgets about the sale.
    #  We remember him the transactions to "watch".
    sale_id = tx.env["sale.order"].search([("name", "=", tx.reference.split("-", 1)[0])]).id
    PaymentProcessing.add_payment_transaction(tx)
    request.session["__website_sale_last_tx_id"] = tx.id
    request.session["sale_order_id"] = sale_id
    request.session["sale_last_order_id"] = sale_id


class PaymentKNET(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[("knet", _("KNET"))])
    knet_tranportal_id = fields.Char(string="Transportal ID",
                                     required_if_provider="knet", groups='base.group_user')
    knet_tranportal_password = fields.Char(string="Transportal Password",
                                           required_if_provider="knet", groups='base.group_user')
    # TODO: Enforce 16 bytes length?
    knet_terminal_resource_key = fields.Char(string="Terminal Resource Key",
                                             required_if_provider="knet", groups='base.group_user')
    knet_callback_base_url = fields.Char(string="Callback Base URL",
                                             required_if_provider="knet", groups='base.group_user')
    knet_use_samesite_workaround = fields.Boolean(string="Use SameSite Workaround", groups="base.group_user")

    def _get_payment_url(self) -> str:
        if self.state == "test":
            return "https://kpaytest.com.kw/kpg/PaymentHTTP.htm?"
        else:
            return "https://www.kpay.com.kw/kpg/PaymentHTTP.htm?"

    def _generate_request_url(self, values: dict) -> str:
        base_url = self.knet_callback_base_url
        callback_url = url_join(base_url, CALLBACK_URL)

        tranportal_id = self.knet_tranportal_id
        track_id = values.get("reference")
        lang = "AR" if values.get("billing_partner_lang", "en_US").split("_")[0] == "ar" else "USA"
        action = "1"

        # TODO: KNET supports 3 decimal points, but Odoo gives us amount as rounded to 2, is this okay?
        amount = values.get("amount")
        amount = _amount_repr(amount)
        currency = CURRENCY_CODES.get(values.get("currency").name, "")

        # Sanity checks.
        if not currency:
            raise ValidationError(_("Your currency is not supported by the KNET Payment system."))
        assert "," not in amount, "Amount can't contain ',' char!"
        assert amount[-3] == ".", "Decimal precision must be 2 digits and separator must be '.' char!"

        raw_str = join_parameters([("id", self.knet_tranportal_id),
                                   ("password", self.knet_tranportal_password),
                                   ("langid", lang),
                                   ("trackid", track_id),
                                   ("amt", amount),
                                   ("currencycode", currency),
                                   ("action", action),
                                   ("responseURL", callback_url),
                                   ("errorURL", callback_url),
                                   ("udf1", "none"),
                                   ("udf2", "none"),
                                   ("udf3", "none"),
                                   ("udf4", "none"),
                                   ("udf5", "none"),
                                   ])
        enc_str = encrypt_data(raw_str, self.knet_terminal_resource_key)
        req_str = join_parameters([("param", "paymentInit"),
                                  ("trandata", enc_str),
                                  ("tranportalId", tranportal_id),
                                  ("responseURL", callback_url),
                                  ("errorURL", callback_url)
                                   ])
        req_str = self._get_payment_url() + req_str

        return req_str

    def knet_form_generate_values(self, values: dict) -> dict:
        values["request_url"] = self._generate_request_url(values)
        return values

    @api.model
    def _create_missing_journal_for_acquirers(self, company=None):
        acquirer_modules = self.env['ir.module.module'].search(
            [('name', 'like', 'payment_%'), ('state', 'in', ('to install', 'installed'))])
        acquirer_names = [a.name.split('_')[-1] for a in acquirer_modules]

        company = company or self.env.company
        acquirers = self.env['payment.acquirer'].search(
            [('provider', 'in', acquirer_names), ('journal_id', '=', False), ('company_id', '=', company.id)])

        journals = self.env['account.journal']
        for acquirer in acquirers.filtered(lambda l: not l.journal_id and l.company_id.chart_template_id):
            acquirer.journal_id = self.env['account.journal'].create(
                acquirer._prepare_account_journal_vals())
            journals += acquirer.journal_id
        return journals


class TrasanctionKNETPayment(models.Model):
    _inherit = 'payment.transaction'

    knet_tx_resp = fields.Char(string="Encrypted Transaction Response", groups='base.group_user')

    @api.model
    def _knet_form_get_tx_from_data(self, data):
        reference = data.get("trackid")
        if not reference:
            raise ValidationError(_("KNET system didn't send a track ID!"))

        tx = self.search([("reference", "=", reference)])
        if len(tx) != 1:
            if not tx:
                err = _("No order found!")
            else:
                err = _("Found multiple orders!")

            _logger.error(err)
            raise ValidationError(err)

        # TODO: Why don't tx'es have times by default?
        if not tx.date:
            tx.date = fields.Datetime.now()

        if tx.acquirer_id.knet_use_samesite_workaround:
            _add_tx_to_current_session(tx)
        return tx

    def _knet_form_validate(self, data):
        error_text = data.get("ErrorText")
        error_code = data.get("Error")
        payment_id = data.get("paymentid")
        trandata = data.get("trandata")

        # Update transaction info.
        self.acquirer_reference = payment_id
        self.date = fields.Datetime.now()
        self.state_message = error_text
        self.knet_tx_resp = trandata

        if error_text or error_code:
            error = _("Gateway did not approve the payment:\n"
                      "{}").format(error_text)
            _logger.error(error)
            self._set_transaction_error(error)
            return False

        dec_data = decrypt_data(trandata, self.acquirer_id.knet_terminal_resource_key)
        dec_data = url_decode(dec_data)
        result = dec_data.get("result")

        if result == "CANCELED":
            _logger.info(_("KNET payment cancelled for tx {}").format(self.reference))
            self._set_transaction_cancel()
            return False

        # TODO: Which results considered "success"?
        #  The docs says anything other than "CAPTURED" is failure but
        #  it never returns that, including on KNET's own examples.
        if result in ("CAPTURED", "PROCESSED"):
            amount = _amount_repr(self.amount)
            paid = _amount_repr(float(dec_data.get("amt")))
            if amount != paid:
                error = _("Payment amount does not match:\n"
                          "Amount to pay: {}, Amount paid: {}").format(amount, paid)
                _logger.error(error)
                self._set_transaction_error(error)

                return False

            _logger.info(_("Validated KNET payment for tx {}: set as done").format(self.reference))
            self._set_transaction_done()
            self._post_process_after_done()
            self.execute_callback()

            return True
        elif result in ("NOT CAPTURED"):
            error = _("Your payment was declined, please try again with different card or contact your bank for further information \nPayment ID: {}").format(dec_data.get("paymentid"))
            # error = _("Payment:\n"
            #           "{}, Payment ID: {}").format(result, dec_data.get("paymentid"))
            _logger.error(error)
            self._set_transaction_error(error)

            return False
        else:
            error = _("Gateway sent unknown result:\n"
                      "{}, Payment ID: {}").format(result, dec_data.get("paymentid"))
            _logger.error(error)
            self._set_transaction_error(error)

            return False

    # Dev One Change: Need to rewrite whole method to change context
    # def _reconcile_after_transaction_done(self):
    #     # Override of '_set_transaction_done' in the 'payment' module
    #     # to confirm the quotations automatically and to generate the invoices if needed.
    #     sales_orders = self.mapped('sale_order_ids').filtered(lambda so: so.state in ('draft', 'sent'))
    #     for tx in self:
    #         tx._check_amount_and_confirm_order()
    #     # send order confirmation mail
    #     sales_orders._send_order_confirmation_mail()
    #     # invoice the sale orders if needed
    #     self._invoice_sale_orders()
    #     res = super(TrasanctionKNETPayment, self)._reconcile_after_transaction_done()
    #     if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice'):
    #         default_template = self.env['ir.config_parameter'].sudo().get_param('sale.default_email_template')
    #         if default_template:
    #             for trans in self.filtered(lambda t: t.sale_order_ids):
    #                 # Dev One Change: company_id.id throws error, so passed company_id record
    #                 ctx_company = {'company_id': trans.acquirer_id.company_id,
    #                                'force_company': trans.acquirer_id.company_id.id,
    #                                'mark_invoice_as_sent': True,
    #                                }
    #                 trans = trans.with_context(ctx_company)
    #                 for invoice in trans.invoice_ids.with_user(SUPERUSER_ID):
    #                     invoice.message_post_with_template(int(default_template), email_layout_xmlid="mail.mail_notification_paynow")
    #     return res

class InvoiceKnet(models.Model):
    _inherit = "account.move"

    def message_post_with_template(self, template_id, email_layout_xmlid=None, auto_commit=False, **kwargs):
        if self.env.context.get('company_id') and isinstance(self.env.context['company_id'], int):
            company = self.env['res.company'].browse(self.env.context['company_id'])
            self = self.with_context(company_id=company)
        return super(InvoiceKnet, self).message_post_with_template(template_id, email_layout_xmlid=email_layout_xmlid, auto_commit=auto_commit, **kwargs)
