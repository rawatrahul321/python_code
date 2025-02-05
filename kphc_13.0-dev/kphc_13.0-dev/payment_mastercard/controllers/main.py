# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
##1###############################################################################
from odoo import http
from odoo.http import request
import werkzeug
import pprint
import logging
_logger = logging.getLogger(__name__)


class WkMasterCardController(http.Controller):

    _returnUrl = "/payment/mastercard/return"
    _cancelUrl = "/payment/mastercard/cancel"
    _errorUrl = "/payment/mastercard/error"

    @http.route([_returnUrl, _cancelUrl, _errorUrl], auth="public", type='http', csrf=False, website=True)
    def mastercard_return(self, **post):
        """ Mastercard"""
        _logger.info(
            'MasterCard: entering form_feedback with post data %s', pprint.pformat(post))
        if post:
            request.env['payment.transaction'].sudo(
            ).form_feedback(post, 'mastercard')
        return werkzeug.utils.redirect('/payment/process')


