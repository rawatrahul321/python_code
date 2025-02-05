# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import json

from odoo import http,  _
from odoo.http import request
from ast import literal_eval

from odoo.addons.website_sale_stock.controllers.main import WebsiteSaleStock


class WebsiteSaleCustom(WebsiteSaleStock):

    # @http.route(['/shop/payment/transaction/',
    #     '/shop/payment/transaction/<int:so_id>',
    #     '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public", website=True)
    # def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
    #     res = super(WebsiteSaleCustom, self).payment_transaction(acquirer_id, save_token=save_token, so_id=so_id, access_token=access_token, token=token, **kwargs)
    #     order = None
    #     if so_id:
    #         env = request.env['sale.order']
    #         domain = [('id', '=', so_id)]
    #         if access_token:
    #             env = env.sudo()
    #             domain.append(('access_token', '=', access_token))
    #         order = env.search(domain, limit=1)
    #     else:
    #         order = request.website.sale_get_order()

    #     if order:
    #         template = request.env.ref('send_email.delivery_email_template', raise_if_not_found=False)
    #         if template:
    #             internalUsers = request.env['res.users'].sudo().search([('share','=', False)]).mapped('partner_id')
    #             template['partner_to'] = ",".join(str(e.id) for e in internalUsers)
    #             template.send_mail(order.id)
    #     return res

    @http.route()
    def payment_transaction(self, *args, **kwargs):
        res = super(WebsiteSaleCustom, self).payment_transaction(*args, **kwargs)

        order = request.website.sale_get_order()
        if order:
            template = request.env.ref('send_email.delivery_email_template', raise_if_not_found=False)
            if template:
                internalUsers = request.env['res.users'].sudo().search([('share','=', False)])
                accounting_team = internalUsers.filtered(lambda user: user.has_group('account.group_account_invoice') or user.has_group('account.group_account_user') or user.has_group('account.group_account_manager')).mapped('partner_id')
                if accounting_team:
                    internalpartners = ",".join(str(e.id) for e in accounting_team)
                    email_values = {
                        'recipient_ids': [(6,0,literal_eval(internalpartners))],
                    }
                    template.sudo().send_mail(order.id,email_values=email_values,)
        return res
