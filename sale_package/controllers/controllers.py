# -*- coding: utf-8 -*-
# from odoo import http


# class SalePackage(http.Controller):
#     @http.route('/sale_package/sale_package/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_package/sale_package/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_package.listing', {
#             'root': '/sale_package/sale_package',
#             'objects': http.request.env['sale_package.sale_package'].search([]),
#         })

#     @http.route('/sale_package/sale_package/objects/<model("sale_package.sale_package"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_package.object', {
#             'object': obj
#         })
