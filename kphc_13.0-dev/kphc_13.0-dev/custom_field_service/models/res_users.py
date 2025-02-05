# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, api, fields, _


class ResUserIn(models.Model):
	_inherit = 'res.users'


	job_position = fields.Char(string="Job Position")
	phone = fields.Char(string="Phone")