# -*- coding: utf-8 -*-
from odoo import http

# class TvpComplementos(http.Controller):
#     @http.route('/tvp_complementos/tvp_complementos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tvp_complementos/tvp_complementos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tvp_complementos.listing', {
#             'root': '/tvp_complementos/tvp_complementos',
#             'objects': http.request.env['tvp_complementos.tvp_complementos'].search([]),
#         })

#     @http.route('/tvp_complementos/tvp_complementos/objects/<model("tvp_complementos.tvp_complementos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tvp_complementos.object', {
#             'object': obj
#         })