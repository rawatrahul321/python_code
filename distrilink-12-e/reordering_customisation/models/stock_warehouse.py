# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models, fields


class Orderpoint(models.Model):
    """ Defines Minimum stock rules. """
    _inherit = 'stock.warehouse.orderpoint'

    recurring_date = fields.Date('Recurring Date', default=fields.Date.today())
