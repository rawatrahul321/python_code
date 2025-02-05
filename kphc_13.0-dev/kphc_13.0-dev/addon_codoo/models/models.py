# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    remark = fields.Text('Remark')

    def _compute_display_name_manual(self):
        for partner in self.env['res.partner'].search([]):
            if partner.company_type == 'person':
                partner.display_name = '%s %s'%(partner.firstname if partner.firstname else ' ',partner.name if partner.name else ' ')
            else:
                partner.display_name = partner.name

    @api.depends('is_company', 'name', 'parent_id.display_name', 'type', 'company_name','firstname')
    def _compute_display_name(self):
        for partner in self:
            if partner.company_type == 'person':
                partner.display_name = '%s %s'%(partner.firstname if partner.firstname else ' ',partner.name if partner.name else ' ')
            else:
                partner.display_name = partner.name

    def name_get(self):
        res_list = []
        for contact in self:
            res_list.append((contact.id, contact.display_name))
        return res_list

class SaleORder(models.Model):
    _inherit = 'sale.order'

    mobile = fields.Char(related='partner_id.mobile')
