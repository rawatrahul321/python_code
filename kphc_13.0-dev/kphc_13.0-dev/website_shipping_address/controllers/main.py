# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from werkzeug.exceptions import Forbidden
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError


class AuthSignupHomeInherit(AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'phone')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()


class WebsiteShipping(WebsiteSale):

    def values_postprocess(self, order, mode, values, errors, error_msg):
        response = super(WebsiteShipping, self).values_postprocess(order, mode, values, errors, error_msg)
        response[0]['addr_nm'] = values.get('addr_nm') # uncomment by Imroz
        response[0]['firstname'] = values.get('firstname')
        response[0]['block'] = values.get('block')
        response[0]['building'] = values.get('building')
        response[0]['apart_number'] = values.get('apart_number')
        response[0]['area_id'] = int(values.get('area_id') or 0)
        response[0]['floor'] = values.get('floor')
        response[0]['avenue'] = values.get('avenue')
        # response[0]['street2'] = values.get('street2')
        response[0]['x_studio_street'] = values.get('street')
        response[0]['email'] = values.get('email')
        response[0]['remark'] = values.get('street2')
        # response[0]['location_type'] = values.get('location_type')
        if response and response[0].get('street'):
            response[0]['street'] = response[0]['street'].replace("\r\n", "").strip()
        return response

    def _get_mandatory_billing_fields(self):
        return ["firstname", "phone","state_id","area_id"]

    # Dev one: remove email from required fields
    def _get_mandatory_shipping_fields(self):
        return ["firstname", "phone","state_id","area_id"]

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):
        res = super(WebsiteShipping, self).address(**kw)
        #cites = request.env['res.city'].search([])
        areas_ids = request.env['res.city.area'].sudo().search([])
        #res.qcontext['cites'] = cites
        res.qcontext['areas_ids'] = areas_ids
        return res


class CustomerPortalInherited(CustomerPortal):

    MANDATORY_BILLING_FIELDS = ["name", "country_id", 'email',
                                "phone", "firstname"]#"area_id"
    OPTIONAL_BILLING_FIELDS = ["zipcode", "vat", "company_name",'apart_number',
                               'addr_nm',  'block', 'street2', 'building',
                               'state_id', 'area_id', 'floor', 'avenue',
                               'location_type', 'street']

    _items_per_page = 20

    @http.route(['/my/address', '/my/address/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_address(self, page=1, date_begin=None, date_end=None, **kw):
        Partner = request.env.user.partner_id
        shippings = Partner.search([
                ("id", "child_of", Partner.commercial_partner_id.ids),
                '|', ("type", "=", "delivery"), ("id", "=", Partner.commercial_partner_id.id)
            ], order='id desc')

        values = {'partner_id': Partner,
                  'shippings': shippings,
                  'user': request.env.user}
        return request.render("website_shipping_address.address_display", values)

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()
        values.update({
            'error': {},
            'error_message': []
        })
        if post:
            print("\n\n\n :: :: :: :: :: ", post)
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                values.update({'zip': values.pop('zipcode', '')})
                values.update({'name': values.get('firstname') + ' ' + values.get('name')})
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([('country_id.name', '=', 'Kuwait')])
        areas_ids = request.env['res.city.area'].sudo().search([])
        first_name = ''
        last_name = ''
        if partner:
            if len(partner.name.split(" ")) > 1:
                name = partner.name.split(" ")
                first_name = name[0]
                lname = name.pop(0)
                last_name = ' '.join(name)
        values.update({
            'first_name': first_name,
            'last_name': last_name,
            'partner': partner,
            'countries': countries,
            'areas_ids': areas_ids,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
        })
        return request.render("portal.portal_my_details", values)
