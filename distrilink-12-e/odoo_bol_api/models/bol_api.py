# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import json
import time
import logging

from odoo import api, models, fields
from odoo.addons.update_stock_api.models.authorization import AuthorizeBolAPI
from datetime import timedelta

logger = logging.getLogger(__name__)

class InhAuthorizeBolAPI(AuthorizeBolAPI):
    def sale_forecast_request(self, method, uri, header_accept, content_type='', params={}, data={}, access_token=None, **kwargs):
        request_kwargs = dict(**kwargs)
        request_data = []
        request_kwargs.update({
            "method": method,
            "url": self.api_url + uri,
            "params": params,
            "data": json.dumps(data)
        })
        if "headers" not in request_kwargs:
            request_kwargs["headers"] = self.session.headers
            request_kwargs["headers"].update({
                "Authorization": "Bearer " + access_token,
                "Accept": header_accept,
                "content-type": content_type
            })
        resp = self.session.request(**request_kwargs)
        # resp.raise_for_status()
        return resp


class BolConnection(models.Model):
    """Defines Minimum stock rules."""
    _inherit = "bol.connection"

    is_processed = fields.Boolean('Is Processed')

    @api.model
    def bol_import_product_rules(self):
        """
        Update the default value of product_min_qty and product_max_qty from bol.com
        """

        connections = self.env['bol.connection'].search([('is_processed', '=', False)], limit=1)
        cron = self.env.ref('odoo_bol_api.bol_ir_cron_scheduler_action')
        if not connections:
            conns = self.env['bol.connection'].search([])
            for con in conns:
                con.is_processed = False
            connections = self.env['bol.connection'].search([('is_processed', '=', False)], limit=1)
        orderpoint_obj = self.env["stock.warehouse.orderpoint"]
        # Get the BOL warehouse and location
        warehouse_id = self.env.ref("channable_api.bol_warehouse")
        location_id = self.env["stock.location"].search(
            [("barcode", "=", "BVWH-STOCK")]
        )

        product_min_qty = 0
        product_max_qty = 0
        count_updated_product = 0
        product_list = []
        message = []
        status = True

        for conn in connections:
            try:
                # Call the API
                login = AuthorizeBolAPI().login(conn.client_id, conn.client_secret)
                api = InhAuthorizeBolAPI()

                # Request an offer export file containing all offers.
                post_offers_data = api.sale_forecast_request(
                    "POST",
                    "/retailer/offers/export",
                    "application/vnd.retailer.v5+json",
                    content_type="application/vnd.retailer.v5+json",
                    data={"format": "CSV"},
                    access_token=login.get('access_token')
                ).json()
                self.env['audit.log'].put_audit_log(
                    cron.name, 'Success', post_offers_data, '')
                if post_offers_data.get('title'):
                    message = [post_offers_data.get('title')]
                logger.info('post_offers_data................%s'%(post_offers_data))
                # Get data from export file response link.
                if post_offers_data.get('links'):
                    time.sleep(7)
                    for link in post_offers_data.get('links'):
                        link_data = api.sale_forecast_request(
                            link.get('method'),
                            link.get('href').split('https://api.bol.com')[1],
                            "application/vnd.retailer.v5+json",
                            content_type="application/vnd.retailer.v5+json",
                            access_token=login.get('access_token')
                        ).json()
                        self.env['audit.log'].put_audit_log(
                            cron.name, 'Success' if link_data.get('status') == 'SUCCESS' else 'Failed', link_data, '')
                        print ('link_data...........', link_data)
                        # link_data = api.sale_forecast_request(
                        #     'GET',
                        #     '/retailer/process-status/%s'%(post_offers_data.get('processStatusId')),
                        #     "application/vnd.retailer.v5+json",
                        #     content_type="application/vnd.retailer.v5+json",
                        #     access_token=login.get('access_token')
                        # ).json()
                        logger.info('link_data................%s'%(link_data))
                        if link_data.get('status') != 'SUCCESS':
                            message = ['Offers not get Success status from Bol.com, get Status: %s'%(link_data.get('status'))]
                        if link_data.get('entityId'):
                            # Retrieve an offer export file containing all offers.
                            get_offers_data = api.sale_forecast_request(
                                "GET",
                                "/retailer/offers/export/%s"%(link_data.get('entityId')),
                                "application/vnd.retailer.v5+csv",
                                content_type="application/x-www-form-urlencoded",
                                access_token=login.get('access_token')
                            ).text
                            # Get sales forecast to estimate the sales expectations on the total bol.com platform
                            # for the requested number of weeks ahead.
                            if 'offerId' in get_offers_data:
                                offer_values = get_offers_data.split('\n')
                                offer_values.pop(0)
                                if offer_values[0] == '':
                                    conn.is_processed = True
                                for value in offer_values:
                                    # value.pop(0)
                                    list_value = value.split(',')
                                    logger.info('list_value................%s'%(list_value))
                                    if len(list_value) > 1:
                                        params = {
                                            "offer-id": list_value[0],
                                            "weeks-ahead": 4,
                                        }
                                        request_data = api.sale_forecast_request(
                                            "GET",
                                            "/retailer/insights/sales-forecast",
                                            "application/vnd.retailer.v5+json",
                                            content_type="application/vnd.retailer.v5+json",
                                            params=params,
                                            access_token=login.get('access_token')
                                        ).json()
                                        self.env['audit.log'].put_audit_log(cron.name,
                                            'Success' if request_data.get('status') == 'SUCCESS' else 'Failed', request_data, '')
                                        logger.info('request_data................%s'%(request_data))
                                        if request_data.get('status') == 429:
                                            time.sleep(7)
                                        product = self.env["product.product"].search(
                                            ['|', ('is_fbb', '=', True), ('is_active_ants', '=', True), ('barcode', '=', list_value[1])])
                                        if product and request_data.get("total"):
                                            total_forecast = request_data.get("total")
                                            min_forecast = total_forecast.get("minimum", 0)
                                            max_forecast = total_forecast.get("maximum", 0)
                                            if min_forecast == 0:
                                                product_min_qty = 1
                                            else:
                                                product_min_qty = round(min_forecast/28*10)

                                            if max_forecast == 10:
                                                product_max_qty = 5
                                            else:
                                                product_max_qty = round(max_forecast + (max_forecast/28*10))

                                            # Update the reordering rule if already exist else create new
                                            reordering_rule_id = orderpoint_obj.search(
                                                [("product_id", "=", product.id)]
                                            )
                                            if reordering_rule_id:
                                                reordering_rule_id.write(
                                                    {
                                                        "product_min_qty": product_min_qty,
                                                        "product_max_qty": product_max_qty,
                                                    }
                                                )
                                            else:
                                                reordering_rule_id = orderpoint_obj.create(
                                                    {
                                                        "warehouse_id": warehouse_id.id,
                                                        "location_id": location_id.id or False,
                                                        "product_id": product.id,
                                                        "product_min_qty": product_min_qty,
                                                        "product_max_qty": product_max_qty,
                                                    }
                                                )
                                            count_updated_product += 1
                                            product_list.append(product.barcode)
                                    else:
                                        conn.is_processed = True
                    if product_list:
                        conn.is_processed = True
            except Exception as e:
                status = False
                message = [e]
        if not message:
            message = ['%s Products reordering Rules are Updated, Products list are %s' % (count_updated_product, product_list)]
        self.env['audit.log'].put_audit_log(cron.name, 'Success' if status == True else 'Failed', '', message)
        self.env['ir.cron.history'].register_cron_history(cron.name, cron.id, message)
