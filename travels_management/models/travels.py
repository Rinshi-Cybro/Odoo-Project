from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo import models, fields, api, _


class TravelsManagement(models.Model):
    _name = 'travels.booking'
    _description = 'Travels Management Bookings'
    _rec_name = 'booking_seq'

    booking_seq = fields.Char('Booking Reference', readonly=True, copy=False,
                              required=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    no_of_passengers = fields.Integer(string="No Of Passengers", default=1, required=True)
    service = fields.Selection([('bus', 'Bus'), ('train', 'Train'), ('flight', 'Flight')], string='Service')
    booking_date = fields.Date(default=fields.Date.today())
    source_location = fields.Many2one('travels.locations', string='Source Location')
    destination_location = fields.Many2one('travels.locations', string='Destination Location')
    travel_date = fields.Datetime()
    expiration_date = fields.Date(compute='_compute_expiration_date', store=True)
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirmed', 'Confirmed'),
                                        ('expired', 'Expired')],
                             string='Status', copy=False, track_visibility='onchange',
                             indux=True, default='draft')
    service_id = fields.Many2one('service.types', string="Service Types")

    @api.depends('booking_date', 'service_id.expiration_period')
    def _compute_expiration_date(self):
        for rec in self:
            rec.expiration_date = datetime.strptime(str(rec.booking_date), '%Y-%m-%d') + relativedelta(
                days=+ rec.service_id.expiration_period)

    @api.model
    def _check_expiry(self):
        today = fields.Date.today()
        for rec in self.env['travels.booking'].search([('state', '=', 'draft'),
                                                       ('expiration_date', '<', today)]):
            rec.state = 'expired'

    @api.model
    def create(self, vals):
        if vals.get('booking_seq', _('New')) == _('New'):
            vals['booking_seq'] = self.env['ir.sequence'].next_by_code('travels.bookings.sequence') or _('New')
            result = super(TravelsManagement, self).create(vals)
            return result

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'


class TravelsLocations(models.Model):
    _name = 'travels.locations'
    _description = 'Travels Locations'
    _rec_name = 'locations_name'

    locations_name = fields.Char(string="Locations")


class ServiceTypes(models.Model):
    _name = 'service.types'
    _description = 'Service Types'
    _rec_name = 'service_name'

    service_name = fields.Char(string='Service Name')

    expiration_period = fields.Integer(string='Expiration Period', help='Expiration period in days')


class VehicleTypes(models.Model):
    _name = 'vehicle.types'
    _description = 'Travels Vehicles'
    _sql_constraints = [('registration_no_unique', 'unique(registration_no)',
                         'Registration Number must be unique')]
    _rec_name = 'name'

    name = fields.Char(store=True)
    registration_no = fields.Char(string='Registration No')
    vehicle_type = fields.Selection([('bus', 'Bus'), ('traveller', 'Traveller'), ('van', 'Van'), ('other', 'Other')],
                                    string='Vehicle Types')
    number_of_Seats = fields.Integer(string='Number of Seats', default=1, required=True)
    facilities_ids = fields.Many2many(string='Facilities')

    def name_get(self):
        res = []
        for rec in self:
            rec.name = ('%s %s' % (rec.registration_no, (dict(rec.fields['vehicle_type'].selection)
                                                         .get(rec.vehicle_type))))
            res.append((rec.id, rec.name))
            return res
