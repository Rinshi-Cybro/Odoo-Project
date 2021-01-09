from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    package_names = fields.Many2many('sale.package', 'package_name', string="Packages")
    package_lines = fields.One2many('sale.package', 'package_id', string='package Lines')


class SalePackage(models.Model):
    _name = "sale.package"
    _description = 'Sale Package'
    _rec_name = 'package_name'

    package_name = fields.Char(string='Package Name', required=True)
    width = fields.Float(string='Package Width')
    height = fields.Float(string='Package Height')
    length = fields.Float(string='Package Length')
    maximum_weight = fields.Float(string='Maximum Weight')
    package_id = fields.Many2one('sale.order', string='Package ID')
