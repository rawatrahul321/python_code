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


class AuthorizeChannableAPI():
    """Main conversation handeling with Channable API v1."""

    def __init__(self, channable):
        """Construction Connection and setup."""
        self.api_token = channable.api_token
        self.api_project_id = channable.api_project_id
        self.api_company_id = channable.api_company_id
        self.api_offset = channable.api_offset

    def get_all_orders(self):
        url = "https://api.channable.com/v1/companies/%s/projects/%s/orders?offset=%s&limit=100"%(
            self.api_company_id, self.api_project_id, self.api_offset)
        headers = {'Authorization': "Bearer {}".format(self.api_token)}
        return requests.get(url, headers=headers,).json()

    def update_offers_stock(self, data):
        request_body = json.dumps(data)
        url = "https://api.channable.com/v1/companies/%s/projects/%s/offers"%(self.api_company_id, self.api_project_id)
        headers = {'Authorization': "Bearer {}".format(self.api_token), 'Content-Type': 'application/json'}
        return requests.post(url, headers=headers, data=request_body).json()

    def update_order_shipment(self, data, order_id):
        request_body = json.dumps(data)
        url = "https://api.channable.com/v1/companies/%s/projects/%s/orders/%s/shipment"%(
            self.api_company_id, self.api_project_id, order_id)
        headers = {'Authorization': "Bearer {}".format(self.api_token), 'Content-Type': 'application/json'}
        return requests.post(url, headers=headers, data=request_body).json()

    def update_order_cancellation(self, order_id):
        url = "https://api.channable.com/v1/companies/%s/projects/%s/orders/%s/cancel"%(
            self.api_company_id, self.api_project_id, order_id)
        headers = {'Authorization': "Bearer {}".format(self.api_token), 'Content-Type': 'application/json'}
        return requests.post(url, headers=headers,).json()


class AuthorizeFTP():
    """Main conversation handeling with FTP Location"""

    def __init__(self, ftp_location, ftp_login, password, folder_path):
        """Construction Connection and setup."""
        self.ftp_location = ftp_location
        self.ftp_login = ftp_login
        self.password = password
        self.folder_path = folder_path

    def ftpConnection(self):
        ftp = FTP(self.ftp_location)
        ftp.login(self.ftp_login, self.password)
        return {'ftp': ftp,
                'ftp_folder_path': self.folder_path,
            }
