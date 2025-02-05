# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    use_as_current_user = fields.Boolean('Use as a Current User for Cron Job')
