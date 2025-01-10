import json

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
import requests

class Property(models.Model):
    _name = "property"
    _description = "Property"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ref = fields.Char(default="New", readonly=1)
    name = fields.Char(string="Property Name", required=True, default="New", size=10, translate=True)
    description = fields.Text(string="Property Description", tracking=1)
    postcode = fields.Char(string="Postcode", required=True)
    date_availability = fields.Date(string="Date Availability", tracking=1)
    expected_selling_date = fields.Date(string="Expected Selling Date")
    is_late = fields.Boolean()
    expected_price = fields.Float(string="Expected Price", digits=(0, 4))
    diff = fields.Float(compute="_compute_diff", string="Difference Price", store=True)
    selling_price = fields.Float(string="Selling Price", digits=(0, 4))
    bedrooms = fields.Integer(string="Bedrooms")
    living_area = fields.Integer(string="Living Area")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage", groups="real_estate.property_manager_group")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (m2)")
    garden_orientation = fields.Selection([
        ('south', 'South'),
        ('north', 'North'),
        ('east', 'East'),
        ('west', 'West'),
    ], default="south", string="Garden Orientation")
    owner_id = fields.Many2one('owner', string="Owner Name")
    owner_phone = fields.Char(related='owner_id.phone', string="Owner Phone")
    owner_address = fields.Char(related='owner_id.address', string="Owner Address")
    client_id = fields.Many2one('client', string="Client Name")
    line_ids = fields.One2many('property.line', 'property_id')
    create_time = fields.Datetime(default=fields.Datetime.now())
    next_time = fields.Datetime(compute="_compute_next_time")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('closed', 'Closed'),
    ], default='draft')
    property_history_ids = fields.One2many('property.history', 'property_id', string="History")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_unique', 'unique("name")', 'This name is exist')
    ]

    @api.constrains('bedrooms')
    def _check_bedroom_greater_zero(self):
        for rec in self:
            if rec.bedrooms == 0:
                raise ValidationError("Please add valid numbers for bedrooms")


    def action_draft(self):
        for rec in self:
            rec.create_history_record(rec.state, 'draft')
            rec.state = 'draft'

    def action_pending(self):
        for rec in self:
            rec.create_history_record(rec.state, 'pending')
            rec.write({
                'state': 'pending'
            })

    def action_sold(self):
        for rec in self:
            rec.create_history_record(rec.state, 'sold')
            rec.state = 'sold'

    # Handle server action closed
    def action_closed(self):
        for rec in self:
            rec.create_history_record(rec.state, 'closed')
            rec.state = 'closed'

    # Handle server action change_state_wizard
    def action_open_change_state_wizard(self):
        for rec in self:
            if rec.state != 'closed':
                raise ValidationError("state is not closed")
            else:
                action = self.env['ir.actions.actions']._for_xml_id('real_estate.change_state_wizard_action')
                action['context'] = {'default_property_id': self.id}  # set default value for property
            return action


    # Handle automated action
    def check_expected_selling_date(self):
        # return all records
        property_ids = self.search([
            ('state', 'in', ['draft', 'pending']),
            ('expected_selling_date', '<', fields.date.today())
        ])
        for rec in property_ids:
            rec.is_late = True

    # Handel sequence
    @api.model
    def create(self, vals):
        res = super(Property, self).create(vals)
        if res.ref == "New":
            res.ref = self.env['ir.sequence'].next_by_code('property_seq')  # method that handle sequence
        return res
    # create records in property_history model
    # "": default value for reason if no reason added
    def create_history_record(self, old_state, new_state, reason=""):
        for rec in self:
            rec.env['property.history'].create({
                'user_id': rec.env.uid,
                'property_id': rec.id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason or "",
                'line_ids': [(0, 0, {'description': line.description, 'area': line.area}) for line in rec.line_ids]
            })
    @api.depends('expected_price', 'selling_price')
    def _compute_diff(self):
        for rec in self:
            rec.diff = rec.expected_price - rec.selling_price

    @api.depends('create_time')
    def _compute_next_time(self):
        for rec in self:
            if rec.create_time:
                rec.next_time = rec.create_time + timedelta(hours=6)
            else:
                rec.next_time = False

    @api.onchange('expected_price', 'selling_price')
    def _onchange_positive_prices(self):
        return {
            'warning': {'title': 'warning', 'message': 'negative value', 'type': 'notification'}
        }

    # method for smart button
    def action_open_related_owner(self):
        # reach to owner action
        action = self.env['ir.actions.actions']._for_xml_id('real_estate.owner_action')
        # reach to owner form view
        view_id = self.env.ref('real_estate.owner_form_view').id
        # add id of owner that form open on it
        action['res_id'] = self.owner_id.id
        # open form view only
        action['views'] = [[view_id, 'form']]
        return action

    # Integrate with another app
    def get_properties(self):
        # to send body data
        payload = dict()
        try:
            # call endpoint generate by app
            response = requests.get("http://127.0.0.1:8069/v1/properties", data=payload)
            if response.status_code == 200:
                print("success")
                print(response)
                # to reach data
                print(response.content)
            else:
                print("fail")
        except Exception as error:
            raise ValidationError(str(error))

    # method handel Excel Reports
    def property_xlsx_reporty(self):
        # handle action to call end point (url action)
        return {
            'type': 'ir.actions.act_url',
            # send data with endpoint using context
            'url': f'/property/excel/report/{self.env.context.get("active_ids")}',
            'target': 'new'
        }


class PropertyLine(models.Model):
    _name = "property.line"

    property_id = fields.Many2one('property', string="Property")
    area = fields.Float(string="Area")
    description = fields.Char(string="Description")
