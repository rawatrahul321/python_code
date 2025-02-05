from logging import getLogger
import werkzeug

from odoo import http
from odoo.http import request

_logger = getLogger(__name__)

CALLBACK_URL = '/payment/knet/callback'


class PaymentKNETController(http.Controller):
    @http.route([CALLBACK_URL], methods=['POST', 'GET'], type='http', auth='public', csrf=False, website=True)
    def lloyds_checkout_success(self, **kwargs):
        _logger.info(f"Got callback from KNET: {kwargs}")
        request.env['payment.transaction'].sudo().form_feedback(kwargs, 'knet')

        # Dev One Change
        # return werkzeug.utils.redirect('/payment/process')
        return request.redirect('/payment/process')
