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

    def create_report_xlx(self):
        data = {
            'model_id': self.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'customer': self.customer.name,
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'travels.report.wizard',
                'options': json.dump(data, default=date_utils.json_default),
                'output_format': 'xlsx',
                'report_name': 'Booking xlsx report'
            },
            'report_type': 'xlsx'
        }

    def get_xlsx_report(self, data, response):
        value = []
        model_id = data['model_id']
        date_from = data['date_from']
        date_to = data['date_to']
        customer = data['customer']
        today = fields.Date.today()

        output = io.BytesIO()
        workbook = xlsxwriter.workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': '12px'})
        cell2_format = workbook.add_format({'align': 'left', 'font_size': '14px'})
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '25px'})
        heading = workbook.add_format({'align': 'center', 'bold': True,
                                       'font_size': '11px'})
        txt = workbook.add_format({'font_size': '10px'})
        subhead = workbook.add_format({'align': 'left', 'bold': True,
                                       'font_size': '11px'})
        date = workbook.add_format({'num_format': 'dd/mm/yyyy',
                                    'font_size': '10px', 'align': 'left'})

        sheet.merge_range('F4:S5', 'Booking Report', head)

        if customer:
            sheet.merge_range('L7:M7', customer, heading)
        if date_from:
            sheet.write('G8', 'From Date', txt)
            sheet.write('H8', data['date_from'], date)
        if date_to:
            sheet.write('P8', 'To Date', txt)
            sheet.write('Q8', data['date_to'], date)

        sheet.write('F10', 'SL No', subhead)
        sheet.merge_range('G10:H10', 'Source Location', subhead)
        sheet.merge_range('J10:L10', 'Destination Location', subhead)
        sheet.merge_range('N10:P10', 'Vehicle Name', subhead)
        sheet.merge_range('R10:S10', 'State', subhead)

        query_start = """SELECT DISTINCT ON (booking.id) booking.id, customer.name,
                        location.locations_name AS source_location, locations.locations_name AS
                        destination_location, vehicle.name AS vehicle, booking.state AS state FROM
                        travels_booking AS booking INNER JOIN res_partner AS customer ON 
                        booking.customer_id = customer.id INNER JOIN travels_locations AS
                        location ON booking.source_location = location.id INNER JOIN 
                        travels_locations AS locations ON booking.destination_location = 
                        locations.id LEFT JOIN vehicle_types AS vehicle ON
                        booking.vehicle_id = vehicle.id"""

        if customer and date_from and date_to:

            query = query_start + """ WHERE customer.name = ('%s') AND
                        CAST(booking.booking_date AS DATE) BETWEEN CAST('%s' AS
                        DATE) AND CAST('%s' AS DATE) AND state NOT IN 
                        ('draft')""" % (customer, date_from, date_to)

        elif not customer and date_from and date_to:

            query = query_start + """ WHERE CAST(booking.booking_date AS DATE)
                            BETWEEN CAST('%s' AS DATE) AND CAST('%s' AS DATE) AND
                            state NOT IN ('draft')""" % (date_from, date_to)

        elif customer and date_from and date_to:

            query = query_start + """ WHERE customer.name = ('%s') AND CAST
                                (booking.booking_date AS DATE) BETWEEN
                                CAST('%s' AS DATE) AND CAST('%s' AS DATE) AND
                                state NOT IN (''draft'')""" % (customer, today, date_to)

        elif customer and date_from and not date_to:

            query = query_start + """ WHERE customer.name = ('%s') AND
                                    CAST(booking.booking_date AS DATE) BETWEEN CAST('%s' AS
                                    DATE) AND CAST('%s' AS DATE) AND state NOT IN
                                    ('draft')""" % (customer, date_from, today)

        elif not customer and date_from and not date_to:

            query = query_start + """ WHERE CAST(booking.booking_date AS DATE)
                                        BETWEEN CAST('%s' AS DATE) AND CAST('%s' AS DATE) AND
                                        state NOT IN ('draft')""" % (date_from, today)

        elif customer:
            query = query_start + """ WHERE customer.name = ('%s') AND state
                                             NOT IN ('draft')""" % customer

        else:

            query = query_start + """ WHERE state NOT IN ('draft')"""

        value.append(model_id)
        self._cr.execute(query, value)
        record = self._cr.dictfetchall()
        print(record)

        row = 10
        col = 4
        index = 1
        for rec in record:
            sheet.write(row, col+1, index, cell2_format)
            sheet.merge_range(row, col + 2, row, col + 3,
                              rec['source_location'], cell_format)
            sheet.merge_range(row, col + 5, row, col + 7,
                              rec['destination_location'], cell_format)
            sheet.merge_range(row, col + 9, row, col + 11,
                              rec['vehicle'], cell_format)
            sheet.merge_range(row, col + 13, row, col + 14,
                              rec['state'], cell_format)

            row += 1
            index += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
