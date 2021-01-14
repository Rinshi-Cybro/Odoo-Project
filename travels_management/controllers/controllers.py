# -*- coding: utf-8 -*-
# from odoo import http


# class TravelsManagement(http.Controller):
#     @http.route('/travels_management/travels_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/travels_management/travels_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('travels_management.listing', {
#             'root': '/travels_management/travels_management',
#             'objects': http.request.env['travels_management.travels_management'].search([]),
#         })

#     @http.route('/travels_management/travels_management/objects/<model("travels_management.travels_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('travels_management.object', {
#             'object': obj
#         })
