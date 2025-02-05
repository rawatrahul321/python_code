# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import requests

class AuthorizeBolAPI():

    def __init__(self, session=None, api_url=None, login_url=None):
        self.api_url = api_url or "https://api.bol.com"
        self.login_url = login_url or "https://login.bol.com"
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def login(self, client_id, client_secret):
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }
        resp = self.session.post(
            self.login_url + "/token",
            auth=(client_id, client_secret),
            data=data,
        )
        resp.raise_for_status()
        token = resp.json()
        self.set_access_token(token["access_token"])
        return token

    def set_access_token(self, access_token):
        self.session.headers.update(
            {
                "Authorization": "Bearer " + access_token,
                "Accept": "application/vnd.retailer.v5+json",
            }
        )

    def request(self, method, uri, pages, params={}, **kwargs):
        request_kwargs = dict(**kwargs)
        request_data = []
        for page in range(1, pages):
            params.update({"page":page})
            request_kwargs.update({
                "method": method,
                "url": self.api_url + uri,
                "params": params,
            })
            if "headers" not in request_kwargs:
                request_kwargs["headers"] = {}

            request_kwargs["headers"].update({
                "content-type": "application/vnd.retailer.v5+json"
            })
            resp = self.session.request(**request_kwargs)
            resp.raise_for_status()
            data = resp.json()
            if data.get('inventory'):
                request_data.extend(data.get('inventory'))
        return request_data
