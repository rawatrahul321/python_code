# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import urllib.parse

from odoo import api, fields, models
from werkzeug import urls
import logging

_logger = logging.getLogger(__name__)


class PaymentAcquirerKnet(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('knet', 'Knet')])
    knet_id = fields.Char(string='Knet ID', required_if_provider='knet', groups='base.group_user')
    knet_password = fields.Char(string='Knet Password', required_if_provider='knet', groups='base.group_user')

    def _get_knet_urls(self, environment):
        """ Knet URLs"""
        if environment == 'prod':
            return {'knet_form_url': 'https://www.knetpay.com.kw/CGW302/servlet/PaymentInitHTTPServlet',
                    'payment_url': 'https://www.knetpay.com.kw/CGW302/hppaction?formAction=com.aciworldwide.commerce.gateway.payment.action.HostedPaymentPageAction&?PaymentID='}
        else:
            return {'knet_form_url': 'https://www.knetpaytest.com.kw/CGW302/servlet/PaymentInitHTTPServlet',
                    'payment_url': 'https://www.knetpaytest.com.kw/CGW302/hppaction?formAction=com.aciworldwide.commerce.gateway.payment.action.HostedPaymentPageAction&?PaymentID='}

    def knet_form_generate_values(self, values):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        knet_values = dict(values,
                           id=self.knet_id,
                           password=self.knet_password,
                           action=1,
                           amt=values['amount'],
                           currencycode=414,
                           langid='USA',
                           responseURL='%s' % urls.url_join(base_url, '/payment/knet/return'),
                           errorURL='%s' % urls.url_join(base_url, '/payment/knet/error'),
                           trackid=values['reference'],
                           acquirer_id=self.id,
                           )
        # test card  4242424242424242
        # PIN: 1111
        return knet_values

    def knet_get_form_action_url(self):
        self.ensure_one()
        knet_url = '/payment/knet/register_order'
        return knet_url


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    knet_payment_id = fields.Char('Knet Payment ID')
    knet_txnid = fields.Char('Knet Transaction ID')

    @api.model
    def _knet_form_get_tx_from_data(self, tx_id):

        tx_ids = self.env['payment.transaction'].search([('id', '=', tx_id)])
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'Knet: received data for reference'
            if not tx_ids:
                error_msg += ': no order found.'
            else:
                error_msg += ': multiple order found.'
            _logger.info(error_msg)
        return tx_ids
