# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################
import datetime

from odoo import api, fields, models, _
from odoo.addons.channable_api.models.authorization import AuthorizeChannableAPI
from odoo.exceptions import UserError

class ChannableConnection(models.Model):
    _name = 'channable.connection'
    _description = 'Channable Connection'

    name = fields.Char('Project Name')
    api_project_id = fields.Char('Project ID')
    api_company_id = fields.Char('Company ID')
    api_token = fields.Text('API Token')
    api_offset = fields.Integer('Offset')
    vendor_shipping_hours = fields.Integer('Vendor Process Hours', default=23)

    def apiConnection(self):
        return AuthorizeChannableAPI(self)

    @api.multi
    def test_channable_connection(self):
        for rec in self:
            connection = rec.apiConnection()
            getDetails = connection.get_all_orders()
            if 'data' in getDetails and getDetails['data'] == None:
                raise UserError(_('Make Sure Channable API Token is Correct!'))
            if 'status' in getDetails and getDetails['status'] == 'error':
                raise UserError(_('Make Sure Your Project ID and Company ID is Correct!'))
            raise UserError(_('Connection Test Succeeded! Everything seems properly set up!'))

    def processChannableCustomer(self, data):
        resPartnerObj = self.env['res.partner']
        channableCustomer = data['customer']
        billing = data['billing']
        country = self.env['res.country'].search(
            [('code', '=', billing['country_code'])])
        billing['type'] = 'invoice'
        billing['country_id'] = country.id
        shipping = data['shipping']
        shipping_country = self.env['res.country'].search(
        [('code', '=', shipping['country_code'])])
        shipping['type'] = 'delivery'
        shipping['country_id'] = shipping_country.id
        childData = [billing, shipping]

        customerName = channableCustomer.get('first_name') if channableCustomer.get('first_name') else ''
        customerName += ' ' + channableCustomer.get('middle_name') if channableCustomer.get('middle_name') else ''
        customerName += ' ' + channableCustomer.get('last_name') if channableCustomer.get('last_name') else ''

        resPartner = resPartnerObj.search(['|', '&',
            ('email', '=', channableCustomer['email']),
            ('phone', '=', channableCustomer['phone']),
            ('name', '=', customerName)
        ], limit=1)
        if not resPartner:
            resPartner = resPartnerObj.create({
                'name': customerName,
                'customer': True,
                'phone': channableCustomer['phone'],
                'mobile': channableCustomer['mobile'],
                'email': channableCustomer['email'],
                'website': channableCustomer['company']
            })
        billing_address = False
        shipping_address = False
        for child in childData:
            childName = child.get('first_name') if child.get('first_name') else ''
            childName += ' ' + child.get('middle_name') if child.get('middle_name') else ''
            childName += ' ' + child.get('last_name') if child.get('last_name') else ''

            resPartnerChild = resPartnerObj.search(['|', '&',
                ('email', '=', child.get('email')),
                ('phone', '=', child.get('phone')),
                ('name', '=', childName),
                ('parent_id', '=', resPartner.id),
                ('type', '=', child.get('type')),
                ('street', '=', child.get('address1')),
                ('street2', '=', child.get('address2'))
            ], limit=1)
            if not resPartnerChild:
                resPartnerChild = resPartner.child_ids.create({
                    'name': childName,
                    'email': child.get('email'),
                    'street': child.get('address1'),
                    'street2': child.get('address2'),
                    'country_id': child.get('country_id'),
                    'city': child.get('city'),
                    'zip': child.get('zip_code'),
                    'type': child.get('type'),
                    'parent_id': resPartner.id,
                    'house_number': child.get('house_number'),
                    'house_number_ext': child['house_number_ext'],
                    'Address_supplement': child['address_supplement']
                })
            if resPartnerChild.type == 'delivery':
                shipping_address = resPartnerChild
            else:
                billing_address = resPartnerChild

        return {'resPartner': resPartner, 'billing_address': billing_address, 'shipping_address': shipping_address}

    def processSaleOrderLine(self, data, order_id):
        for line in data['products']:
            intCode = line.get('id', '')
            barCode = line.get('ean', '')
            product_id = None
            if intCode:
                product_id = self.env['product.product'].search([
                    ('default_code', '=', line['id']),
                    # ('barcode', '=', line['ean'])
                ], limit=1)
            if barCode and not product_id:
                product_id = self.env['product.product'].search([
                    ('barcode', '=', line['ean'])
                ], limit=1)
            if not product_id:
                product_id = self.env['product.template'].create({
                    'name': line['title'],
                    'sale_ok': True,
                    'channable_product_id': line['id'],
                    'list_price': line['price'],
                    'type': 'product',
                    'taxes_id': False,
                    'is_review_product': True,
                    'barcode': barCode,
                    'default_code': line['id']
                }).product_variant_id
            if not product_id.channable_product_id:
                product_id.write({'channable_product_id': line['id']})
            saleOrderLine = self.env['sale.order.line'].create({
                'product_id': product_id.id,
                # 'name': product_id.name or ' ',
                'order_id': order_id.id,
                # 'uom_id': product_id.uom_id.id,
                'product_uom_qty': float(line['quantity']),
                'price_unit': line['price'],
                'channable_product_commission': line['commission'] or 0.0
            })
            if order_id.channable_channel_id.description == 'Amazon DE':
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
            if order_id.channable_channel_id.description == 'Amazon FR':
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

    def processChannel(self, data):
        channelObj = self.env['channable.order.channel']
        channel = channelObj.search([('channel_id', '=', data['channel_id'])])
        if not channel:
            channel = channelObj.create({
                'name': data['channel_name'],
                'channel_id': data['channel_id'],
                'description': data['data']['extra']['label'] if 'label' in data['data']['extra'] else ''
            })
        return channel

    def syncOrders(self):
        conns = self.env['channable.connection'].search([])
        orderCount = 0
        channableCount = 0
        errorCount = 0
        for conn in conns:
            channableApi = conn.apiConnection()
            getChannableOrders = channableApi.get_all_orders()
            saleOrderObj = self.env['sale.order']
            channableOrders = getChannableOrders.get('orders', '')
            if channableOrders:
                for order in channableOrders:
                    saleOrder = saleOrderObj.search([
                        ('channable_order_id', '=', order['id'])
                    ])
                    if not saleOrder:
                        customer = self.processChannableCustomer(order['data'])
                        channel = self.processChannel(order)
                        saleOrder = saleOrderObj.create({
                            'channable_order_id': order['id'],
                            'partner_id': customer.get('resPartner').id,
                            'channable_commission': order['data']['price']['commission'] or 0.0,
                            'order_platform_id': order['platform_id'],
                            'channable_channel_id': channel.id,
                            'channable_order_date': order['created'],
                            'partner_invoice_id': customer.get('billing_address').id,
                            'partner_shipping_id': customer.get('shipping_address').id,
                            'channable_project_id': conn.api_project_id
                        })

                        saleOrderLine = self.processSaleOrderLine(order['data'], saleOrder)
                        if not saleOrder.is_channable_error_order:
                            saleOrder.write({'state': 'channable_order'})
                            channableCount += 1
                        if saleOrder.is_channable_error_order:
                            errorCount += 1
                        orderCount += 1

        cron = self.env.ref('channable_api.ir_cron_sync_orders')
        message = ['%s Orders are Created Success Fully %s with Channable Order state and %s with Error Order State' % (
                            orderCount, channableCount, errorCount)]
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def channableStockUpdate(self):
        conns = self.search([])
        for conn in conns:
            channableApi = conn.apiConnection()
            last15Min = datetime.datetime.now() - datetime.timedelta(minutes=15)
            stockQunants = self.env['stock.quant'].search([('write_date', '>=', last15Min), ('quantity', '>', 0)])
            product_ids = list(set([stock.product_id.id for stock in stockQunants]))
            offerData = []
            productCount = 0
            if product_ids:
                for product in self.env['product.product'].browse(product_ids):
                    value = {'id': product.channable_product_id,
                            'title': product.name,
                            'price': product.lst_price,
                            'stock': product.qty_available}
                    offerData.append(value)
                    productCount += 1
            postStock = channableApi.update_offers_stock(offerData)
            if 'status' in postStock and postStock['status'] == 'success':
                cron = self.env.ref('channable_api.ir_cron_channable_stock_update')
                message = ['%s Product Stocks are Updated from Odoo to Channable' % (productCount)]
                self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)

    def shipping_update_to_channable_23hours(self):
        conns = self.env['channable.connection'].search([])
        shippingCount = 0
        order_list = []
        for conn in conns:
            orders = self.env['sale.order'].search([
                ('state', '=', 'vendor_process'),
                ('vendor_process_date', '<=', datetime.datetime.now()-datetime.timedelta(hours=conn.vendor_shipping_hours)),
                ('channable_project_id', '=', conn.api_project_id)
            ])
            for order in orders:
                channableApi = conn.apiConnection()
                shipment_order = channableApi.update_order_shipment({}, order.channable_order_id)
                if shipment_order.get('status') == 'success':
                    order.is_empty_shipping = True
                    shippingCount += 1
                    order_list.append(order.name)
        cron = self.env.ref('channable_api.ir_cron_23hours_shipping_update')
        message = ['%s orders %s are shipped with empty shipping details' % (shippingCount, order_list)]
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
