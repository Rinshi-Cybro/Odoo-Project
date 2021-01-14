from odoo import models, fields, api, _


class TravelsManagement(models.Model):
    _name = 'travels.booking'
    _description = 'Travels Management Bookings'
    _rec_name = 'booking_reference'

    booking_reference = fields.Char('Booking Reference', readonly=True, copy=False,
                                    required=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    no_of_passengers = fields.Integer(string="No Of Passengers", default=1, required=True)
    service_id = fields.Many2one('travels.service.types', string='Service')
    booking_date = fields.Date(default=fields.Date.today())
    source_location_id = fields.Many2one('travels.locations')
    travel_date = fields.Datetime()
    # expiration_date = fields.Date(compute='_compute_expiration_date', store=True)
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirmed', 'Confirmed'),
                                        ('expired', 'Expired')],
                             string='Status', copy=False, track_visibility='onchange',
                             indux=True, default='draft')
