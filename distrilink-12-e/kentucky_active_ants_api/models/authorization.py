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

class AuthorizeKentuckyActiveAntsApi(AuthorizeActiveAntsApi):

    def __init__(self,url, username, password):
        AuthorizeActiveAntsApi.__init__(self,url, username, password)

    def post_shipment_byordertype(self, api_token, order_type_id):
        url = self.api_url + '/v2/shipment/byordertype'
        headers = {'Authorization': "Bearer {}".format(api_token), 'Content-Type': 'application/json'}
        request_body = json.dumps({'OrderTypes': [order_type_id]})
        return requests.post(url, headers=headers, data=request_body).json()
