# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models, api, _

class ChannelEngineCountryCode(models.Model):
    _name = 'channelengine.country.code'
    _description = 'ChannelOrder Country Code'

    name = fields.Char('ChannelOrderCountryCode')
    code = fields.Char('Transformation Code')
