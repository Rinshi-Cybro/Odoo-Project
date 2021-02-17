from odoo import models, fields, api


class TravelsReportPrint(models.AbstractModel):
    _name = 'report.travels_management.print_travels_report'
    _description = 'Booking Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """in this function can access the data returned from the button click function"""
        model_id = data['model_id']
        date_from = data['date_from']
        date_to = data[' date_to']
        customer_id = data['customer_id']
        today = fields.Date.today()

        value = []
        query_start = """SELECT DISTINCT ON (booking.id) booking.id, customer.name,
                location.location_id AS source_location, location.location_id AS
                destination_location, vehicle.name AS vehicle, booking.state AS state FROM
                travels_booking AS booking INNER JOIN """