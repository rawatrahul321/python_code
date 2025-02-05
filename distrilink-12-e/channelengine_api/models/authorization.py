# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import json
import requests
from ftplib import FTP
import datetime
import random
import hashlib
import logging

logger = logging.getLogger(__name__)

class AuthorizeChannelEngine():
    """Main conversation handeling with ChannelEngine Product API"""
    def __init__(self, url, secret_key):
        """Construction Connection and setup."""
        self.url = url
        self.secret_key = secret_key

    def get_fbm_orders(self):
        """Get FBM Orders from ChannelEngine with New status"""
        url = self.url + 'api/v2/orders/new'
        params = {
            'apikey': self.secret_key
        }
        logger.info("FBM Orders Response..., %s" %(requests.get(url, params)))
        return requests.get(url, params).json()

    def ack_fbm_order(self, merchant_order_no, order_id):
        """Acknowledge FBM orders to ChannelEngine"""
        url = self.url + 'api/v2/orders/acknowledge?apikey=%s'%(self.secret_key)
        headers = {'accept': 'application/json', 'Content-Type': 'application/json-patch+json'}
        ack_data = {
            'MerchantOrderNo': merchant_order_no,
            'OrderId': order_id
        }
        request_body = json.dumps(ack_data)
        return requests.post(url, headers=headers, data=request_body).json()

    def get_fbb_fba_orders(self, hours=1, minutes=00):
        """Get FBB/FBA orders from ChannelEngine with Shipped Status"""
        url = self.url + 'api/v2/orders'
        last_hour_date = datetime.datetime.now() - datetime.timedelta(hours = hours, minutes = minutes)
        params = {
            'apikey': self.secret_key,
            'statuses': 'SHIPPED',
            'fulfillmentType': 'ONLY_CHANNEL',
            'fromCreatedAtDate': last_hour_date.strftime('%m-%d-%Y %H:%M:%S')
        }
        logger.info("FBB/FBA Orders Response..., %s" %(requests.get(url, params)))
        return requests.get(url, params).json()

    def update_offer_stock(self, data):
        """Update Offer Stock from Odoo to ChannelEngine"""
        url = self.url + 'api/v2/offer?apikey=%s'%(self.secret_key)
        request_body = json.dumps(data)
        headers = {'accept': 'application/json', 'Content-Type': 'application/json-patch+json'}
        return requests.put(url, headers=headers, data=request_body).json()

    def create_order_shipment(self, data):
        """Create Shipment from Odoo to ChannelEngine Order"""
        url = self.url + 'api/v2/shipments?apikey=%s'%(self.secret_key)
        request_body = json.dumps(data)
        headers = {'accept': 'application/json', 'Content-Type': 'application/json-patch+json'}
        return requests.post(url, headers=headers, data=request_body).json()

    def update_order_cancellation(self, data):
        """Cancel Order from Odoo to ChannelEngine"""
        url = self.url + 'api/v2/cancellations?apikey=%s'%(self.secret_key)
        request_body = json.dumps(data)
        headers = {'accept': 'application/json', 'Content-Type': 'application/json-patch+json'}
        return requests.post(url, headers=headers, data=request_body).json()

    def get_fbm_order_returns(self):
        """Get all returns created by the channel"""
        url = self.url + 'api/v2/returns/merchant/new'
        params = {
            'apikey': self.secret_key
        }
        return requests.get(url, params).json()

    def get_fbb_fba_order_returns(self, hours=1):
        """Get FBB/FBA orders from ChannelEngine with Shipped Status"""
        url = self.url + 'api/v2/returns/merchant'
        last_hour_date = datetime.datetime.now() - datetime.timedelta(hours = hours)
        params = {
            'apikey': self.secret_key,
            'statuses': 'RECEIVED',
            'fulfillmentType': 'ONLY_CHANNEL',
        }
        return requests.get(url, params).json()

    def update_return_recieved(self, data):
        """Mark a return as received from Odoo to ChannelEngine."""
        url = self.url + 'api/v2/returns?apikey=%s'%(self.secret_key)
        request_body = json.dumps(data)
        headers = {'accept': 'application/json', 'Content-Type': 'application/json-patch+json'}
        return requests.put(url, headers=headers, data=request_body).json()

    def create_fbm_order_returns(self, data):
        """Create Return from Odoo CN to ChannelEngine Order"""
        url = self.url + 'api/v2/returns/merchant?apikey=%s'%(self.secret_key)
        request_body = json.dumps(data)
        headers = {'accept': 'application/json', 'Content-Type': 'application/json-patch+json'}
        return requests.post(url, headers=headers, data=request_body).json()
