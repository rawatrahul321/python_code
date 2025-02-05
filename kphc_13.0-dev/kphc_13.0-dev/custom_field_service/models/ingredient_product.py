# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, api, fields, _

class IngredientProduct(models.Model):
    _name = 'ingredient.product'
    _description = 'ingredient product'

    name = fields.Char(string="Name")


class IngredientUom(models.Model):
    _name = 'ingredient.uom'
    _description = 'ingredient uom'

    name = fields.Char(string="Name") 
