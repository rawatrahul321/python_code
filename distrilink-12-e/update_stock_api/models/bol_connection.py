# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging

from odoo import models, fields, api, _
from odoo.addons.update_stock_api.models.authorization import AuthorizeBolAPI
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class bolConnection(models.Model):
    _name = 'bol.connection'
    _description = 'Bol Connection'

    name = fields.Char('Title')
    client_id = fields.Char('Client ID')
    client_secret = fields.Char('Client Secret')
    pages = fields.Integer(default=10)

    @api.multi
    def test_bol_connection(self):
        try:
            AuthorizeBolAPI().login(self.client_id, self.client_secret)
        except Exception as e:
            raise UserError(_('Make Sure Client Id and Client Secret Are Valid. %s')%e)
        raise UserError(_('Connection Test Succeeded! Everything seems properly set up!'))

    def syncStockFromBol(self):
        connections = self.env['bol.connection'].search([])
        cron = self.env.ref('update_stock_api.ir_cron_sync_fbb_stock')
        count_updated_product = []
        message = []
        status = True
        for conn in connections:
            api = AuthorizeBolAPI()
            try:
                login = api.login(conn.client_id, conn.client_secret)
                request_data = api.request('GET', '/retailer/inventory', conn.pages)
                logger.info('request_data................%s'%(request_data))
                self.env['audit.log'].put_audit_log(cron.name, 'Success', request_data, '')
                # request_data = request.json()
                for data in request_data:
                    product = self.env['product.product'].search([('barcode', '=', data.get('ean')), ('is_fbb', '=', True)])
                    if product:
                        location_id = self.env['stock.location'].search([('barcode', '=', 'BVWH-STOCK')])
                        changeQty = self.env['stock.change.product.qty'].create({
                            'product_id': product.id,
                            'new_quantity': data.get('regularStock'),
                            'location_id': location_id.id or False
                        })
                        changeQty.change_product_qty()
                        product.write({'qty_available': data.get('regularStock')})
                        count_updated_product.append(product.name)
            except Exception as e:
                status = False
                message = [e]
        if not message:
            message = ['%s Products stock are updated' % (count_updated_product)]
        self.env['audit.log'].put_audit_log(
            cron.name, 'Success' if status == True else 'Failed', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
