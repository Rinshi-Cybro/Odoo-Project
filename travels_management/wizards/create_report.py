from odoo import models, fields
import time

import json

import datetime

import io

from odoo.exceptions import ValidationError

from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter

except ImportError:

    import xlsxwriter


class TravelsReport(models.TransientModel):
    _name = "travels.report.wizard"
    _description = "Travels Management PDF Report"

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    customer = fields.Many2one('res.partner', string='Customer Name')

    def print_pdf(self):
        print("lllooo")
        data = {
            'model_id': self.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'customer': self.customer.name,
        }

        return self.env.ref('travels_management.print_report_pdf').report_action(self, data=data)
