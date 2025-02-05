# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import json
import requests
import datetime
import random
import hashlib


class AuthorizeSaleslayer():
    """Main conversation handeling with Saleslayer Product API"""
    def __init__(self, url, code, secret_key, hours):
        """Construction Connection and setup."""
        self.url = url
        self.code = code
        self.secret_key = secret_key
        self.last_modified_hours = hours

    def get_request(self):
        time = datetime.datetime.timestamp(datetime.datetime.now())
        unique = random.randrange(1, 100)
        codification_key = self.code + self.secret_key + str(int(time)) + str(unique)
        sha2key = hashlib.sha256(codification_key.encode())
        params = {
            'code': self.code,
            'time': int(time),
            'unique': unique,
            'key256': sha2key.hexdigest(),
            'same_parent_variants': 1,
            'group_category_id': 1,
            'last_update': datetime.datetime.now() - datetime.timedelta(hours=self.last_modified_hours)
        }
        request = requests.get(self.url, params)
        return request.json()
