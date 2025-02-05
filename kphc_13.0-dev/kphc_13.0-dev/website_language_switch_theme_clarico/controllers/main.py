# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.base.models.ir_ui_view import keep_query
from odoo.addons.http_routing.models.ir_http import url_for

class EmiproThemeBase(http.Controller):

    @http.route('/website_language_switch_theme_clarico/get_template_content', type='http', methods=['POST'], auth="public", website=True)
    def get_template_content(self, **kwargs):
        editable = request.website.is_publisher()
        translatable = editable and request.context.get('lang') != request.env['ir.http']._get_default_lang().code
        editable = not translatable and editable

        top_menu_switch = request.website.viewref("website_language_switch.top_menu_switch")
        if not top_menu_switch.active:
            return ""
        values = {
            'url': kwargs.get('url'),
            'request': request,
            'is_frontend_multilang': request.is_frontend_multilang,
            'website': request.website,
            'languages': request.env['res.lang'].get_available(),
            'translatable': translatable,
            'editable': editable,
            'keep_query': keep_query,
            'url_for': url_for,
        }
        content = request.env.ref("website_language_switch_theme_clarico.language_switch").render(values)
        return content
