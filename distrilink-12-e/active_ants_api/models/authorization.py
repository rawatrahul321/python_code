# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import json
import requests


class AuthorizeActiveAntsApi():
    """Main conversation handeling with Channable API v1."""

    def __init__(self, url, username, password):
        """Construction Connection and setup."""
        self.api_url = url
        self.api_username = username
        self.api_password = password

    def getApiToken(self):
        url = self.api_url + '/token'
        payload = "grant_type=password&username=%s&password=%s"%(self.api_username, self.api_password)
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
        }
        return requests.request("POST", url, data=payload, headers=headers)

    def getSettings(self, api_token):
        url = self.api_url + '/settings/get'
        headers = {'Authorization': "Bearer {}".format(api_token)}
        return requests.get(url, headers=headers).json()

    def postOrders(self, api_token, data):
        url = self.api_url + '/order/add'
        headers = {'Authorization': "Bearer {}".format(api_token), 'Content-Type': 'application/json'}
        request_body = json.dumps(data)
        return requests.post(url, headers=headers, data=request_body).json()

    def getShipments(self, api_token):
        url = self.api_url + '/v2/shipment/get'
        headers = {'Authorization': "Bearer {}".format(api_token)}
        return requests.get(url, headers=headers).json()

    def ackShipmetsupdate(self, api_token, shipment_data):
        url = self.api_url + '/v2/shipment/sync'
        headers = {'Authorization': "Bearer {}".format(api_token), 'Content-Type': 'application/json'}
        request_body = json.dumps(shipment_data)
        return requests.post(url, headers=headers, data=request_body).json()

    def postProducts(self, api_token, product_data):
        url = self.api_url + '/product/add'
        headers = {'Authorization': "Bearer {}".format(api_token), 'Content-Type': 'application/json'}
        request_body = json.dumps(product_data)
        return requests.post(url, headers=headers, data=request_body).json()

    def postProductEdit(self, api_token, product_data):
        url = self.api_url + '/product/edit'
        headers = {'Authorization': "Bearer {}".format(api_token), 'Content-Type': 'application/json'}
        request_body = json.dumps(product_data)
        return requests.post(url, headers=headers, data=request_body).json()

    def getProducts(self, api_token, sku):
        url = self.api_url + '/v2/product/search?sku=' + sku
        headers = {'Authorization': "Bearer {}".format(api_token)}
        return requests.get(url, headers=headers).json()
