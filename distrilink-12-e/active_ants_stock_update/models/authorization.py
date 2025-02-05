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

class AuthorizeActiveAntsApiStock(AuthorizeActiveAntsApi):

    def __init__(self,url, username, password):
        AuthorizeActiveAntsApi.__init__(self,url, username, password)

    def get_product_stock(self, api_token):
        url = self.api_url + '/stock/bulk/true'
        headers = {'Authorization': "Bearer {}".format(api_token)}
        response = requests.get(url, headers=headers).json()
        return requests.get(url, headers=headers).json()
