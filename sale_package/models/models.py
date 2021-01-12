from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    package_names = fields.Many2many('sale.package', string="Packages")
    package_lines = fields.One2many('sale.package', 'package_id', string='package Lines')

    @api.onchange('package_names')
    def _onchange_package_names(self):
        for rec in self:
            lines = [(5, 0, 0)]
            print("output", self.package_names)
            for line in self.package_names:
                print("line", line)
                values = {'package_name': line.package_name,
                          'width': line.width,
                          'height': line.height,
                          'length': line.length,
                          'maximum_weight': line.maximum_weight}
                print("values", values)
                lines.append((0, 0, values))
                print("lines", lines)
            self.package_lines = lines
            print("self.package_lines", self.package_lines)
            rec.package_lines = lines


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
