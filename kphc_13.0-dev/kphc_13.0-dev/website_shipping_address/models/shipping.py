# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
# To get current url instead of base url
from odoo.http import request
from werkzeug import urls


class ResArea(models.Model):
    _name = "res.city.area"

    name = fields.Char(translate=True, required=True)
    code = fields.Char()
    state_id = fields.Many2one("res.country.state", string="City")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # addr_nm = fields.Char()
    addr_nm = fields.Selection(
        selection=[('doctor', _('Doctor')), ('social_media', _('Social media')), ('friend', _('Friend')),
                   ('personal_search', _('Personal search'))], string='Reach us by')
    firstname = fields.Char()
    block = fields.Char()
    building = fields.Char()
    floor = fields.Char()
    avenue = fields.Char()
    apart_number = fields.Char()
    location_type = fields.Char()
    area_id = fields.Many2one("res.city.area", string="Area")


class Respart(models.Model):
    _inherit = 'res.country.state'
    name = fields.Char(string='State Name', required=True, translate=True,
                       help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton')


# Modified By Krutarth on 5th March
class WebsiteInherit(models.Model):
    _inherit = "website"

    enable_custom_address = fields.Boolean('Custom Address', default=False)


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    def _get_signup_url_for_action(self, action=None, view_type=None, menu_id=None, res_id=None, model=None):
        """ generate a signup url for the given partner ids and action, possibly overriding
            the url state components (menu_id, id, view_type) """

        res = dict.fromkeys(self.ids, False)
        for partner in self:
            base_url = partner.sudo().get_base_url()
            # when required, make sure the partner has a valid signup token
            if self.env.context.get('signup_valid') and not partner.user_ids:
                partner.sudo().signup_prepare()

            route = 'login'
            # the parameters to encode for the query
            query = dict(db=self.env.cr.dbname)
            signup_type = self.env.context.get('signup_force_type_in_url', partner.sudo().signup_type or '')
            if signup_type:
                route = 'reset_password' if signup_type == 'reset' else signup_type

            if partner.sudo().signup_token and signup_type:
                query['token'] = partner.sudo().signup_token
            elif partner.user_ids:
                query['login'] = partner.user_ids[0].login
            else:
                continue  # no signup token, no user, thus no signup url!

            fragment = dict()
            base = '/web#'
            if action == '/mail/view':
                base = '/mail/view?'
            elif action:
                fragment['action'] = action
            if view_type:
                fragment['view_type'] = view_type
            if menu_id:
                fragment['menu_id'] = menu_id
            if model:
                fragment['model'] = model
            if res_id:
                fragment['res_id'] = res_id

            if fragment:
                query['redirect'] = base + urls.url_encode(fragment)

            res[partner.id] = urls.url_join(request.httprequest.url_root,
                                            "/web/%s?%s" % (route, urls.url_encode(query)))
        return res
