# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models

class ChannableOrderChannel(models.Model):
    _inherit = 'channable.order.channel'

    channel_no = fields.Char('Channel No.')
