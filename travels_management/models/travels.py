from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from datetime import datetime
from odoo import models, fields, api, _


class TravelsManagement(models.Model):
    _name = 'travels.booking'
    _description = 'Travels Management Bookings'
    _rec_name = 'booking_seq'

    @api.depends('package_line_ids.sub_total')
    def _compute_total(self):
        """Computing the all total"""
        for rec in self:
            for line in rec.package_line_ids:
                rec.total_amount += line.sub_total
            return rec.total_amount

    def create_invoice(self):
        """Create booking Invoice"""
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'invoice_date': self.booking_date,
            'partner_id': self.customer_id.id,
            'invoice_date_due': self.travel_date,
            'l10n_in_gst_treatment': 'consumer',
            'journal_id': 1,
            'invoice_line_ids': []
        })
        if self.service_id.id == 1:
            invoice['invoice_line_ids'] = [(0, 0, {'name': line.service,
                                                   'quantity': line.quantity,
                                                   'price_unit': line.amount})
                                           for line in self.package_line_ids]
        else:
            invoice['invoice_line_ids'] = [(0, 0, {'name': self.booking_seq +
                                                           self.service_id.service_name,
                                                   'price_unit': self.fees})]
        return {
            'name': 'Customer Invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
        }

    booking_seq = fields.Char('Booking Reference', readonly=True, copy=False,
                              required=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string="Customer", required=True)
    no_of_passengers = fields.Integer(string="No Of Passengers", default=1, required=True)
    service = fields.Selection([('bus', 'Bus'), ('train', 'Train'), ('flight', 'Flight')], string='Service')
    booking_date = fields.Date(default=fields.Date.today())
    source_location = fields.Many2one('travels.locations', string='Source Location')
    destination_location = fields.Many2one('travels.locations', string='Destination Location')
    travel_date = fields.Datetime()
    fees = fields.Integer(string='Fees')
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id,
                                  required=True)
    expiration_date = fields.Date(compute='_compute_expiration_date', store=True)
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('confirmed', 'Confirmed'),
                                        ('expired', 'Expired')],
                             string='Status', copy=False, track_visibility='onchange',
                             index=True, default='draft')
    total_amount = fields.Monetary(compute='_compute_total', string='Total')
    service_id = fields.Many2one('service.types', string="Service Types")
    package_line_ids = fields.One2many('charge.lines', 'package_id', string='Package Estimate Amount')
    vehicle_id = fields.Many2one('vehicle.types', string='Vehicle')

    @api.depends('booking_date', 'service_id.expiration_period')
    def _compute_expiration_date(self):
        """Computing the expiration date"""
        for rec in self:
            rec.expiration_date = datetime.strptime(str(rec.booking_date), '%Y-%m-%d') + relativedelta(
                days=+ rec.service_id.expiration_period)

    @api.model
    def _check_expiry(self):
        """Checking for the expiry date and changing the state to expiry"""
        today = fields.Date.today()
        for rec in self.env['travels.booking'].search([('state', '=', 'draft'),
                                                       ('expiration_date', '<', today)]):
            rec.state = 'expired'

    @api.model
    def create(self, vals):
        """Creating booking sequence"""
        if vals.get('booking_seq', _('New')) == _('New'):
            vals['booking_seq'] = self.env['ir.sequence'].next_by_code('travels.bookings.sequence') or _('New')
            result = super(TravelsManagement, self).create(vals)
            return result

    def action_confirm(self):
        """Changing the state to Confirmed"""
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
    _description = 'To add the Vehicle Details'
    _sql_constraints = [('registration_no_unique', 'unique(registration_no)',
                         'Registration Number must be unique')]

    name = fields.Char(string='Name', compute='name_get', store=True)
    registration_no = fields.Char(string='Registration No', copy=False, required=True)
    vehicle_type = fields.Selection([('bus', 'Bus'), ('traveller', 'Traveller'),
                                     ('van', 'Van'), ('other', 'Other')],
                                    string='Vehicle Types', required=True)
    number_of_Seats = fields.Integer(string='Number of Seats')
    facilities_ids = fields.Many2many('travels.facilities')
    # date = fields.Date(string='Date')
    starting_date = fields.Date(string='Starting Date')
    ending_date = fields.Date(string='Ending Date')
    charge_line_ids = fields.One2many('charge.lines', 'charge_id', string="Vehicle Charges")

    def name_get(self):
        res = []
        for rec in self:
            rec.name = ('%s %s' % (rec.registration_no, (dict(rec._fields['vehicle_type'].selection)
                                                         .get(rec.vehicle_type))))
            res.append((rec.id, rec.name))
            return res


class Facilities(models.Model):
    _name = 'travels.facilities'
    _description = 'Create Facilities'
    _rec_name = 'facilities'

    facilities = fields.Char(string='Facilities')


class VehicleChargeLines(models.Model):
    _name = 'charge.lines'
    _description = 'Charge Lines'

    service = fields.Char(string="Service")
    quantity = fields.Integer(string="Quantity", default='1')
    unit = fields.Many2one('uom.uom', string="Unit")
    amount = fields.Integer(string="Amount")
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id,
                                  required=True)
    charge_id = fields.Many2one('vehicle.types', string="Charge ID")
    sub_total = fields.Float(compute='_compute_sub_total', string='Sub Total')
    estimation_id = fields.Many2one('tour.packages', string="Estimation ID")
    package_id = fields.Many2one('travels.booking', string="Packages ID")

    @api.depends('quantity', 'amount')
    def _compute_sub_total(self):
        """Computing the sub total"""
        for rec in self:
            rec.sub_total = rec.quantity * rec.amount


class TourPackages(models.Model):
    _name = 'tour.packages'
    _description = 'Tour Packages Details'
    _rec_name = 'package_seq'

    package_seq = fields.Char('Tour Package Reference', readonly=True, copy=False,
                              required=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    quotation_date = fields.Date(string='Quotation Date')
    source_location = fields.Many2one('travels.locations', string='Source Location')
    destination_location = fields.Many2one('travels.locations', string='Destination Location')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    number_of_travellers = fields.Integer(string='Number Of Travellers')
    facility_ids = fields.Many2many('travels.facilities', string='Facilities')
    vehicle_type = fields.Selection([('bus', 'Bus'), ('traveller', 'Traveller'),
                                     ('van', 'Van'), ('other', 'Other')],
                                    string='Vehicle Types', required=True)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')],
                             string='Status', default='draft')
    vehicle_id = fields.Many2one('vehicle.types', string='Vehicle')
    estimated_km = fields.Float(string='Estimated KM')
    estimation_line_id = fields.One2many('charge.lines', 'estimation_id', string='Estimation Lines')
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id,
                                  required=True)
    total_amount = fields.Monetary(compute='_compute_total', string='Total')
    service_id = fields.Many2one('service.types', string="Service", default=1)

    @api.onchange('vehicle_id')
    def onchange_vehicle_charge(self):
        """Add a vehicle charge line"""
        lines = [(5, 0, 0)]
        for line in self.vehicle_id.charge_line_ids:
            val = {'service': line.service,
                   'quantity': line.quantity,
                   'amount': line.amount,
                   'sub_total': line.sub_total}
            lines.append((0, 0, val))
            self.estimation_line_id = lines

    def action_confirm(self):
        vehicles = self.env['tour.packages'].search([(
            'vehicle_id', '=', self.vehicle_id.id
        )])
        self.vehicle_id.starting_date = self.start_date
        self.vehicle_id.ending_date = self.end_date
        for rec in vehicles:
            if ((rec.start_date < self.start_date < rec.end_date) or
                    (rec.start_date < self.end_date < rec.end_date) or
                    (self.start_date < rec.start_date < self.end_date) or
                    (self.start_date < rec.end_date < self.end_date)):
                raise UserError('Choose Another Vehicle!')
        self.state = 'confirmed'

        values = [(0, 0, {'service': line.service, 'quantity': line.quantity,
                          'amount': line.amount, 'sub_total': line.sub_total})
                  for line in self.estimation_line_id]

        booking = self.env['travels.booking'].create({
            'customer_id': self.customer_id.id,
            'booking_date': self.quotation_date,
            'no_of_passengers': self.number_of_travellers,
            'travel_date': self.start_date,
            'source_location': self.source_location.id,
            'destination_location': self.destination_location.id,
            'service_id': self.service_id.id,
            'package_line_ids': values,
            'vehicle_id': self.vehicle_id.id
        })

    @api.depends('estimation_line_id.sub_total')
    def _compute_total(self):
        """Computing the all total"""
        for rec in self:
            for line in self.estimation_line_id:
                rec.total_amount += line.sub_total
            return rec.total_amount

    @api.model
    def create(self, vals):
        """Creating tour packages sequence"""
        if vals.get('package_seq', _('New')) == _('New'):
            vals['package_seq'] = self.env['ir.sequence'].next_by_code('tour.packages.sequence') or _('New')
            result = super(TourPackages, self).create(vals)
        return result

    @api.onchange('vehicle_type', 'number_of_travellers', 'facility_ids')
    def onchange_vehicle_id(self):
        """Set vehicle_id list domain"""
        for rec in self:
            return {'domain': {'vehicle_id': [('vehicle_type', '=', self.vehicle_type),
                                              ('number_of_Seats', '>=', self.number_of_travellers),
                                              ('facilities_ids.id', 'in', self.facility_ids.ids)]}}

    # def action_confirm(self):
    #     """Changing the state to Confirmed"""
    #     for rec in self:
    #         rec.state = 'confirmed'
