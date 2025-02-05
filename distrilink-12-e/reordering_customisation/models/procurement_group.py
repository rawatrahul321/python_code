# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import models, fields


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    def _get_orderpoint_domain(self, company_id=False):
        domain = super(ProcurementGroup, self)._get_orderpoint_domain(company_id=company_id)
        domain.append(('recurring_date', '<=', fields.Date.today()))
        return domain
