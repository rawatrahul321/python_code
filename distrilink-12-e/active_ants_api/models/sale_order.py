# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_active_ants_order = fields.Boolean('Is Actvie Ants Order')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('channable_order', 'ChannelEngine Order'),
        ('sent', 'Quotation Sent'),
        ('review', 'Error Order'),
        ('vendor_process', 'Vendor Process'),
        ('ants_order', 'Ants Order'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')
