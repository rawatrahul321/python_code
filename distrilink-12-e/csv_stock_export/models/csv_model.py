# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           # 
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import api, fields, models


class CsvModel(models.Model):
    _name = "csv.stock"
    _description = "CSV Stock Model"


    csv_file = fields.Binary('CSV File')
    file_name = fields.Char('Name')

