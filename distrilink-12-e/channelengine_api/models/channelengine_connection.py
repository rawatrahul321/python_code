# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging
import datetime
import pandas

from odoo import api, fields, models, _
from odoo.addons.channelengine_api.models.authorization import AuthorizeChannelEngine
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.safe_eval import safe_eval

logger = logging.getLogger(__name__)


class ChannelEngineConnection(models.Model):
    _name = 'channelengine.connection'
    _description = 'ChannelEngine Connection'

    name = fields.Char('Channel Name')
    api_key = fields.Char('API Key')
    url = fields.Char('URL')

    def processChannableCustomer(self, data):
        resPartnerObj = self.env['res.partner']
        billing = data.get('BillingAddress')
        country = self.env['res.country'].search(
            [('code', '=', billing.get('CountryIso'))])
        billing['type'] = 'invoice'
        billing['country_id'] = country.id
        shipping = data.get('ShippingAddress')
        shipping_country = self.env['res.country'].search(
        [('code', '=', shipping.get('CountryIso'))])
        shipping['type'] = 'delivery'
        shipping['country_id'] = shipping_country.id
        childData = [billing, shipping]
        company = False

        if shipping.get('CompanyName'):
            company = self.env['res.partner'].search([('name', '=', shipping.get('CompanyName'))], limit=1)
            if not company:
                company = self.env['res.partner'].create({'name': shipping.get('CompanyName')})

        customerName = billing.get('FirstName') if billing.get('FirstName') else ''
        customerName += ' ' + billing.get('LastName') if billing.get('LastName') else ''

        resPartner = resPartnerObj.search(['|', '&',
            ('email', '=', data.get('Email')),
            ('phone', '=', data.get('Phone')),
            ('name', '=', customerName)
        ], limit=1)
        if not resPartner:
            resPartner = resPartnerObj.create({
                'name': customerName,
                'customer': True,
                'phone': data.get('Phone'),
                'email': data.get('Email'),
                'parent_id': company.id if company else False,
            })
        resPartner.write({
            'first_name': billing.get('FirstName') if billing.get('FirstName') else '',
            'last_name': billing.get('LastName') if billing.get('LastName') else '',
            'parent_id': company.id if company else False,
        })
        billing_address = False
        shipping_address = False
        for child in childData:
            childName = child.get('FirstName') if child.get('FirstName') else ''
            childName += ' ' + child.get('LastName') if child.get('LastName') else ''

            resPartnerChild = resPartnerObj.search(['|', '&',
                ('email', '=', data.get('Email')),
                ('name', '=', childName),
                ('parent_id', '=', resPartner.id),
                ('type', '=', child.get('type')),
                ('street', '=', child.get('StreetName')),
                # ('street2', '=', child.get('Line2'))
            ], limit=1)
            if not resPartnerChild:
                resPartnerChild = resPartner.child_ids.create({
                    'name': childName,
                    'email': data.get('Email'),
                    'street': child.get('StreetName'),
                    # 'street2': child.get('Line2'),
                    'country_id': child.get('country_id'),
                    'city': child.get('City'),
                    'zip': child.get('ZipCode'),
                    'type': child.get('type'),
                    'parent_id': resPartner.id,
                    'house_number': child.get('HouseNr'),
                    'house_number_ext': child.get('HouseNrAddition'),
                    'ce_company_name': child.get('CompanyName')
                })
            resPartnerChild.write({
                'first_name': child.get('FirstName') if child.get('FirstName') else '',
                'last_name': child.get('LastName') if child.get('LastName') else '',
                'ce_company_name': child.get('CompanyName') or ''
            })
            if resPartnerChild.type == 'delivery':
                shipping_address = resPartnerChild
            else:
                billing_address = resPartnerChild

        return {'resPartner': resPartner, 'billing_address': billing_address, 'shipping_address': shipping_address}

    def processSaleOrderLine(self, lines, order_id):
        for line in lines:
            barCode = line.get('Gtin', '')
            product_id = None
            if barCode:
                product_id = self.env['product.product'].search([
                    '|', ('active', '=', False), ('active', '=', True),
                    ('barcode', '=', line['Gtin'])
                ], limit=1)
            if not product_id:
                product_id = self.env['product.template'].create({
                    'name': line.get('Description'),
                    'sale_ok': True,
                    'channable_product_id': line.get('ChannelProductNo'),
                    'marchant_product_no': line.get('MerchantProductNo'),
                    'list_price': line.get('UnitPriceInclVat'),
                    'type': 'product',
                    'taxes_id': False,
                    'is_review_product': True,
                    'barcode': barCode,
                }).product_variant_id
            if not product_id.channable_product_id:
                product_id.write({'channable_product_id': line.get('ChannelProductNo')})
            if not product_id.marchant_product_no:
                product_id.write({'marchant_product_no': line.get('MerchantProductNo')})
            saleOrderLine = self.env['sale.order.line'].create({
                'product_id': product_id.id,
                'order_id': order_id.id,
                'product_uom_qty': float(line.get('Quantity')),
                'price_unit': line.get('UnitPriceInclVat'),
            })
            if order_id.channable_channel_id.description == 'Amazon.de (v2)':
                tax = self.env['account.tax'].search([('amount', '=', '16.0000'), ('type_tax_use', '=', 'sale')], limit=1)
                if not tax:
                    tax = self.env['account.tax'].create({
                        'name': '16%',
                        'amount_type': 'percent',
                        'amount': 16.0000,
                        'type_tax_use': 'sale',
                        'description': '16%',
                        'price_include': True
                    })
                saleOrderLine.write({'tax_id': [(6, 0, [tax.id])]})
            if order_id.channable_channel_id.description == 'Amazon.fr (v2)':
                tax = self.env['account.tax'].search([('amount', '=', '20.0000'), ('type_tax_use', '=', 'sale')], limit=1)
                if not tax:
                    tax = self.env['account.tax'].create({
                        'name': '20%',
                        'amount_type': 'percent',
                        'amount': 20.0000,
                        'type_tax_use': 'sale',
                        'description': '20%',
                        'price_include': True
                    })
                saleOrderLine.write({'tax_id': [(6, 0, [tax.id])]})
        return True

    def processChannel(self, channel_name, channel_no, global_name, channel_order_no):
        channelObj = self.env['channable.order.channel']
        channel = channelObj.search([('channel_id', '=', channel_order_no)])
        if not channel:
            channel = channelObj.create({
                'name': channel_name,
                'channel_id': channel_order_no,
                'description': global_name or '',
                'channel_no': channel_no
            })
        return channel

    def processOrder(self, orderData):
        saleOrderObj = self.env['sale.order']
        channel = self.processChannel(
            orderData.get('ChannelName'), orderData.get('ChannelId'),
            orderData.get('GlobalChannelName'), orderData.get('ChannelOrderNo'))

        saleOrder = saleOrderObj.search([
            ('channable_channel_id', '=', channel.id)
        ])
        if not saleOrder:
            customer = self.processChannableCustomer(orderData)
            order_date = orderData.get('OrderDate').split('+')[0].split('.')[0]
            saleOrder = saleOrderObj.create({
                'channable_order_id': orderData.get('Id'),
                'partner_id': customer.get('resPartner').id,
                'channable_channel_id': channel.id,
                'channable_order_date': datetime.datetime.strptime(order_date, '%Y-%m-%dT%H:%M:%S').strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'partner_invoice_id': customer.get('billing_address').id,
                'partner_shipping_id': customer.get('shipping_address').id,
            })
            self.processSaleOrderLine(orderData.get('Lines'), saleOrder)
        return saleOrder

    def syncFbmOrders(self):
        conns = self.env['channelengine.connection'].search([])
        cron = self.env.ref('channelengine_api.ir_cron_sync_channelengine_orders')
        orderCount = []
        channelengineCount = []
        errorCount = []
        status = True
        message = []
        for con in conns:
            authorize = AuthorizeChannelEngine(con.url, con.api_key)
            orders = authorize.get_fbm_orders()
            logger.info(_("FBM Orders..., %s" %(orders)))
            if orders.get('Success') != True:
                status = False
                message = [orders.get('Message')]
            self.env['audit.log'].put_audit_log(cron.name, 'Success' if orders.get('Success') == True else 'Failed', orders, '')
            if orders.get('Content'):
                for order in orders.get('Content'):
                    saleOrder = self.processOrder(order)
                    if not saleOrder.is_channable_error_order and saleOrder.state == 'draft':
                        saleOrder.write({'state': 'channable_order'})
                        channelengineCount.append(saleOrder.name)
                    if saleOrder.is_channable_error_order:
                        errorCount.append(saleOrder.name)
                    orderCount.append(saleOrder.name)
                    if saleOrder and saleOrder.marketplace_id == order.get('ChannelOrderNo'):
                        ack = authorize.ack_fbm_order(order.get('ChannelOrderNo'), order.get('Id'))
                        self.env['audit.log'].put_audit_log(cron.name, 'Success', 'ack', '')
        if not message:
            message = ['%s Orders are Created Success Fully %s with ChannelEngine Order state and %s with Error Order State' % (
                                orderCount, channelengineCount, errorCount)]
        self.env['audit.log'].put_audit_log(cron.name, 'Success' if status == True else 'Failed', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def syncFbbFbaOrders(self):
        conns = self.env['channelengine.connection'].search([])
        cron = self.env.ref('channelengine_api.ir_cron_sync_fbb_fba_channelengine_orders')
        fbb_fba_orders = []
        hours = 1
        minutes = 00
        status = True
        message = []
        cron_history = self.env['ir.cron.history'].search(
            [('cron', '=', cron.id)], limit=1, order='id desc')
        if cron_history.status == 'fail':
            last_success = self.env['ir.cron.history'].search([
                ('cron', '=', cron.id), ('status', '=', 'success')], limit=1, order='id desc')
            all_failed_history = self.env['ir.cron.history'].search([
                ('cron', '=', cron.id), ('date', '>', last_success.date), ('date', '<=', cron_history.date)])
            for failed_his in all_failed_history:
                minutes += 20
            pd_datetime = pandas.to_datetime(minutes, unit='m')
            hours = pd_datetime.hour
            minutes = pd_datetime.minute
        for con in conns:
            invMessage = ''
            orders = AuthorizeChannelEngine(con.url, con.api_key).get_fbb_fba_orders(hours, minutes)
            logger.info(_("FBB/FBA Orders..., %s" %(orders)))
            if orders.get('Success') != True:
                status = False
                message = [orders.get('Message')]
            self.env['audit.log'].put_audit_log(cron.name, 'Success' if orders.get('Success') == True else 'Failed', orders, '')
            if orders.get('Content'):
                for order in orders.get('Content'):
                    saleOrder = self.processOrder(order)
                    if not saleOrder.is_channable_error_order and saleOrder.state == 'draft':
                        saleOrder.write({'state': 'channable_order'})
                    for line in saleOrder.order_line:
                        if (line.product_id.is_fba and
                            (line.order_id.channable_channel_id and 'Amazon' in line.order_id.channable_channel_id.name)):
                            wh_location = self.env['stock.location'].search([('name', '=', 'WH')])
                            stock_quant = self.env['stock.quant'].search([
                                ('product_id', '=', line.product_id.id),
                                ('location_id.usage', '=', 'internal'),
                                ('location_id.location_id', '!=', wh_location.id)
                            ], limit=1)
                            warehouse = False
                            if stock_quant:
                                warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', stock_quant.location_id.id)])
                            if warehouse:
                                saleOrder.warehouse_id = warehouse.id
                            else:
                                saleOrder.warehouse_id = self.env.ref('channable_api.amazon_eu_warehouse').id
                            saleOrder.is_fbm_order = True
                        elif (line.product_id.is_fbb and
                            (line.order_id.channable_channel_id and 'Bol' in line.order_id.channable_channel_id.name)):
                            saleOrder.warehouse_id = self.env.ref('channable_api.bol_warehouse').id
                            saleOrder.is_fbm_order = True
                    if saleOrder.is_fbm_order:
                        fbb_fba_orders.append(saleOrder.name)
                        saleOrder.action_confirm()
                        invoice_id = False
                        for picking in saleOrder.picking_ids:
                            try:
                                res = picking.button_validate()
                                invoice_id = saleOrder.action_invoice_create()
                            except Exception as e:
                                if picking.state != 'done':
                                    saleOrder.write({'delivery_validate_error': e})
                                    self.env['audit.log'].put_audit_log(cron.name, 'Failed', '', e)
                        if invoice_id:
                            invoice = self.env['account.invoice'].browse(invoice_id)
                            invoice.action_invoice_open()
                            invoice.sale_order_id = saleOrder.id
                            invoice.send_invoice_mail()
                            journal = self.env['account.journal'].search([('is_pay_channable_invoice', '=', True)], limit=1)
                            if journal:
                                if invoice.state == 'open':
                                    invoice.moveInvoiceToPaid(invoice, journal)
                            else:
                                invMessage = '%s Invoice is not go to Paid state because journal are not Configured'%invoice.number
                                self.env['audit.log'].put_audit_log(cron.name, 'Failed', '', invMessage)
        if not message:
            message = ['%s Orders are FBB/FBA Orders' % (fbb_fba_orders)]
            if invMessage:
                message.append(invMessage)
        self.env['audit.log'].put_audit_log(cron.name, 'Success' if status == True else 'Failed', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def channelEngineStockUpdate(self):
        conns = self.env['channelengine.connection'].search([])
        cron = self.env.ref('channelengine_api.ir_cron_channelengine_stock_update')
        for conn in conns:
            last15Min = datetime.datetime.now() - datetime.timedelta(minutes=15)
            stockQunants = self.env['stock.quant'].search([('write_date', '>=', last15Min), ('quantity', '>', 0)])
            product_ids = list(set([stock.product_id.id for stock in stockQunants]))
            offerData = []
            productCount = 0
            if product_ids:
                for product in self.env['product.product'].browse(product_ids):
                    value = {'MerchantProductNo': product.marchant_product_no,
                            'Price': product.lst_price,
                            'Stock': product.qty_available}
                    offerData.append(value)
                    productCount += 1
            postStock = AuthorizeChannelEngine(conn.url, conn.api_key).update_offer_stock(offerData)
            self.env['audit.log'].put_audit_log(
                cron.name, 'Success' if postStock.get('Success') == True else 'Failed', postStock, '')
            if postStock.get('Success') == True:
                message = ['%s Product Stocks are Updated from Odoo to ChannelEngine' % (productCount)]
                self.env['audit.log'].put_audit_log(
                    cron.name, 'Success', '', message[0])
                self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def processRefund(self, marketplace_id, reason, mr_return_no, ch_return_no, cust_comment, mr_comment, return_id):
        invoice = self.env['account.invoice'].search([
            ('marketplace_id', '=', marketplace_id),
            ('state', 'not in', ('draft', 'cancelled')),
            ('type', '=', 'out_invoice')])
        if invoice:
            old_cr_note = self.env['account.invoice'].search([
                ('type', '=', 'out_refund'),
                # ('return_id', '=', return_id),
                ('refund_invoice_id', 'in', invoice.ids)
            ])
            if not old_cr_note:
                refund_id = self.env['account.invoice.refund'].create({
                    'date_invoice': datetime.datetime.now(),
                    'description': reason,
                    'filter_refund': 'refund'
                })
                cr_nt = self.createInvoiceRefund(refund_id, invoice)
                credit_note = self.env['account.invoice'].browse(cr_nt)
                credit_note.write({
                    'marchant_return_no': mr_return_no,
                    'channel_return_no': ch_return_no,
                    'customer_comment': cust_comment or '',
                    'merchant_comment': mr_comment,
                    'return_id': return_id,
                    'return_reason': reason,
                    'manual_returns': False
                })
                return credit_note
        return True

    def createInvoiceRefund(self, refund_id, invoice, mode='refund'):
        xml_id = False

        for form in refund_id:
            created_inv = []
            date = False
            description = False
            for inv in invoice:
                refund = form._get_refund(inv, mode)
                created_inv.append(refund.id)
            return created_inv
        return True

    def processStockReturns(self, marketplace_id, lines):
        sale_order = self.env['sale.order'].search([('marketplace_id', '=', marketplace_id)])
        if sale_order:
            for picking in sale_order.picking_ids:
                returnPicking = self.env['stock.return.picking'].create({
                    'picking_id': picking.id,
                    'location_id': picking.location_id.id,
                    'original_location_id': picking.location_id.id,
                    'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id
                })
                for move in picking.move_lines:
                    if move.state == 'cancel':
                        continue
                    if move.scrapped:
                        continue
                    for line in lines:
                        product = self.env['product.product'].search([('marchant_product_no', '=', line.get('MerchantProductNo'))])
                        if move.product_id.id == product.id:
                            product_return_moves = self.env['stock.return.picking.line'].create({
                                'product_id': move.product_id.id,
                                'quantity': line.get('Quantity'),
                                'wizard_id': returnPicking.id,
                                'move_id': move.id,
                                'uom_id': move.product_id.uom_id.id
                            })
                            logger.info(_("product_return_moves..., %s" %(product_return_moves)))
                logger.info(_("returnPicking..., %s, %s" %(returnPicking, returnPicking.product_return_moves)))
                self.env['audit.log'].put_audit_log('Stock Returns in Odoo', 'Success', '',
                    'returnPicking: %s, ProductReturnMoves: %s'%(returnPicking, returnPicking.product_return_moves))
                if returnPicking and returnPicking.product_return_moves:
                    return returnPicking._create_returns()
                return False

    def syncFbmOrderReturns(self):
        conns = self.env['channelengine.connection'].search([])
        cron = self.env.ref('channelengine_api.ir_cron_channelengine_fbm_order_returns')
        return_order_count = 0
        status = True
        message = []
        for conn in conns:
            returnOrders = AuthorizeChannelEngine(conn.url, conn.api_key).get_fbm_order_returns()
            self.env['audit.log'].put_audit_log(
                cron.name, 'Success' if returnOrders.get('Success') == True else 'Failed', returnOrders, '')
            if returnOrders.get('Success') != True:
                status = False
                message = [returnOrders.get('Message')]
            for order in returnOrders.get('Content'):
                cr = self.processRefund(order.get('ChannelOrderNo'), order.get('Reason'), order.get('MerchantReturnNo'),
                    order.get('ChannelReturnNo'), order.get('CustomerComment'), order.get('MerchantComment'), order.get('Id'))
                # remove this comment if customer want to set credit note in open state
                # if not isinstance(cr, bool):
                #     cr.action_invoice_open()
                return_order_count += 1
        if not message:
            message = ['%s Orders are FBM Return Orders' % (return_order_count)]
        self.env['audit.log'].put_audit_log(
                cron.name, 'Success' if status == True else 'Failed', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def syncFbbFbaOrderReturns(self):
        conns = self.env['channelengine.connection'].search([])
        cron = self.env.ref('channelengine_api.ir_cron_channelengine_fbb_fba_order_returns')
        invMessage = ''
        return_order_count = 0
        status = True
        message = []
        for conn in conns:
            returnOrders = AuthorizeChannelEngine(conn.url, conn.api_key).get_fbb_fba_order_returns()
            self.env['audit.log'].put_audit_log(
                cron.name, 'Success' if returnOrders.get('Success') == True else 'Failed', returnOrders, '')
            if returnOrders.get('Success') != True:
                status = False
                message = [returnOrders.get('Message')]
            logger.info(_("FBB/FBA Return Orders..., %s" %(returnOrders)))
            for order in returnOrders.get('Content'):
                cr = conn.processRefund(order.get('ChannelOrderNo'), order.get('Reason'), order.get('MerchantReturnNo'),
                    order.get('ChannelReturnNo'), order.get('CustomerComment'), order.get('MerchantComment'), order.get('Id'))
                logger.info(_("cr......., %s" %(cr)))
                if not isinstance(cr, bool):
                    cr.action_invoice_open()
                    cr.send_invoice_mail()
                    journal = self.env['account.journal'].search([('is_pay_channable_invoice', '=', True)], limit=1)
                    if journal:
                        if cr.state == 'open':
                            cr.moveInvoiceToPaid(cr, journal)
                    else:
                        invMessage = '%s Invoice is not go to Paid state because journal are not Configured'%cr.number
                        self.env['audit.log'].put_audit_log(cron.name, 'Failed', '', invMessage)
                    new_picking_id = conn.processStockReturns(order.get('ChannelOrderNo'), order.get('Lines'))
                    if new_picking_id:
                        pick = self.env['stock.picking'].browse(new_picking_id[0])
                        if pick:
                            pick.button_validate()
                    return_order_count += 1
        if not message:
            message = ['%s Orders are FBB/FBA Return Orders' % (return_order_count)]
            if invMessage:
                message.append(invMessage)
        self.env['audit.log'].put_audit_log(cron.name, 'Success' if status == True else 'Failed', '', message[0])
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
