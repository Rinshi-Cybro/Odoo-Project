from odoo import models, fields, api


class TravelsReportPrint(models.AbstractModel):
    _name = 'report.travels_management.print_travels_report'
    _description = 'Booking Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """in this function can access the data returned from the button click function"""
        model_id = data['model_id']
        date_from = data['date_from']
        date_to = data['date_to']
        customer = data['customer']
        today = fields.Date.today()

        value = []
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

        elif not customer and not date_from and date_to:

            query = query_start + """ WHERE CAST(booking.booking_date AS DATE)
                                 <= CAST('%s' AS DATE) AND state NOT IN
                                 ('draft')""" % date_to

        elif customer:
            query = query_start + """ WHERE customer.name = ('%s') AND state
                                     NOT IN ('draft')""" % customer

        else:

            query = query_start + """ WHERE state NOT IN ('draft')"""

        value.append(model_id)
        self._cr.execute(query, value)
        record = self._cr.dictfetchall()
        print(record)

        return {
            'docs': record,
            'date_from': date_from,
            'date_to': date_to
        }
