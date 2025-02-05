# -*- coding: utf-8 -*-
# from odoo import http


# class AddonCodoo(http.Controller):
#     @http.route('/addon_codoo/addon_codoo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/addon_codoo/addon_codoo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('addon_codoo.listing', {
#             'root': '/addon_codoo/addon_codoo',
#             'objects': http.request.env['addon_codoo.addon_codoo'].search([]),
#         })

#     @http.route('/addon_codoo/addon_codoo/objects/<model("addon_codoo.addon_codoo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('addon_codoo.object', {
#             'object': obj
#         })
