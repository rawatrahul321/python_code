# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import json
import requests,os
from ...active_ants_api.models.authorization import AuthorizeActiveAntsApi

class AuthorizeActiveAntsApiReplenish(AuthorizeActiveAntsApi):

    def __init__(self,url, username, password):
        AuthorizeActiveAntsApi.__init__(self,url, username, password)

    def post_purchase_orders(self, api_token, data):
        url = self.api_url + '/purchaseorder/add'
        headers = {'Authorization': "Bearer {}".format(api_token), 'Content-Type': 'application/json'}
        request_body = json.dumps(data)
        return requests.post(url, headers=headers, data=request_body).json()

    def get_stock_mutation(self, api_token):
        url = self.api_url + '/v2/stockmutation/get'
        headers = {'Authorization': "Bearer {}".format(api_token)}
        response = requests.get(url, headers=headers).json()
        return requests.get(url, headers=headers).json()

    def ack_stock_mutations(self, api_token, mutation_data):
        url = self.api_url + '/v2/stockmutation/sync'
        headers = {'Authorization': "Bearer {}".format(api_token), 'Content-Type': 'application/json'}
        request_body = json.dumps(mutation_data)
        return requests.post(url, headers=headers, data=request_body).json()
