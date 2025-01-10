from odoo import models, fields
class Owner(models.Model):
    _name = "owner"

    name = fields.Char(string="Owner Name", required=True)
    phone = fields.Char(string="Owner Phone", required=True)
    address = fields.Char(string="Owner Address")
    property_ids = fields.One2many('property', 'owner_id')
