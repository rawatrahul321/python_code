# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import werkzeug
import urllib.parse
import requests
from odoo import http
from odoo.http import request
from werkzeug import urls

# from odoo.addons.payment.models.payment_acquirer import create_missing_journal_for_acquirers


_logger = logging.getLogger(__name__)


class KnetController(http.Controller):

    @http.route(['/payment/knet/register_order'], type='http', auth='public', csrf=False)
    def knet_register_order(self, **post):
        _logger.info('View Passing Parameters %s', pprint.pformat(post))
        acquirer = request.env['payment.acquirer'].sudo().browse(int(post.pop('acquirer_id')))
        url = acquirer._get_knet_urls(acquirer.environment)
        PT = request.env['payment.transaction'].sudo().search([('reference', '=', post.get('trackid'))])
        if PT.knet_payment_id:
            url = url['payment_url'] + PT.knet_payment_id
            return werkzeug.utils.redirect(url)

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        datas = {
            'id': post.get('id'),
            'password': post.get('password'),
            'action': post.get('action'),
            'amt': post.get('amt'),
            'langid': post.get('langid'),
            'currencycode': post.get('currencycode'),
            'trackid': post.get('trackid'),
            'responseURL': post.get('responseURL'),
            'errorURL': post.get('errorURL'),
        }
        response = requests.request("POST", url['knet_form_url'], data=datas, headers=headers)
        if response.status_code == 200:
            payment_url = response.content
            _logger.info('View Passing Parameters %s', pprint.pformat(response.content))
            result = payment_url.split(':', 1)
            PT.knet_payment_id = result[0]
            return werkzeug.utils.redirect(result[1] + 'PaymentID=' + result[0])

        if response.status_code != 200:
            _logger.exception('Knet: request parameters are missing')
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            return werkzeug.utils.redirect('%s' % urls.url_join(base_url, '/'))

    @http.route(['/payment/knet/error'], type='http', method=['POST'], auth='public', csrf=False)
    def knet_error(self, **post):
        _logger.info('Knet: entering form_feedback with post data %s', pprint.pformat(post))
        if post and post.get('PaymentID'):
            tx = request.env['payment.transaction'].sudo().search([('knet_payment_id', '=', post.get('PaymentID'))])
            tx.state = 'error'
            request.env['payment.transaction'].sudo().form_feedback(tx.id, 'knet')
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        return werkzeug.utils.redirect('%s' % urls.url_join(base_url, '/shop/payment/validate'))

    @http.route(['/payment/knet/return'], type='http', method=['POST'], auth='public', csrf=False)
    def knet_return(self, **post):
        _logger.info('Knet: entering form_feedback with post data %s', pprint.pformat(post))
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        if post.get('result') == 'CAPTURED' and post.get('paymentid'):
            tx = request.env['payment.transaction'].sudo().search([('knet_payment_id', '=', post.get('paymentid'))])
            tx.state = 'done'
            tx.knet_txnid = post.get('tranid')
            request.env['payment.transaction'].sudo().form_feedback(tx.id, 'knet')
            print ('REDIRECT=' + base_url + '/shop/payment/validate')
            return 'REDIRECT=' + base_url + '/shop/payment/validate'
        elif post.get('NOT CAPTURED') and post.get('paymentid'):
            tx = request.env['payment.transaction'].sudo().search([('knet_payment_id', '=', post.get('paymentid'))])
            tx.state = 'error'
            tx.knet_txnid = post.get('tranid')
            request.env['payment.transaction'].sudo().form_feedback(tx.id, 'knet')
            print ('REDIRECT=' + base_url + '/shop/payment/validate')
            return 'REDIRECT=' + base_url + '/shop/payment/validate'
        else:
            tx = request.env['payment.transaction'].sudo().search([('knet_payment_id', '=', post.get('paymentid'))])

            tx.state = 'error'
            tx.knet_txnid = post.get('tranid')
            request.env['payment.transaction'].sudo().form_feedback(tx.id, 'knet')
            return 'REDIRECT=' + base_url + '/shop/payment/validate'
        print ('REDIRECT=' + base_url + '/shop')
        return 'REDIRECT=' + base_url + '/shop'

 #     {'auth': u'783312',
 # 'eci': u'7',
 # 'paymentid': u'669979541172500',
 # 'postdate': u'0907',
 # 'ref': u'725011466650',
 # 'responsecode': u'00',
 # 'result': u'CAPTURED',
 # 'trackid': u'SO224',
 # 'tranid': u'3269526541172500'}
