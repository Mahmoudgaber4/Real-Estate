from odoo import models, fields
class Client(models.Model):
    _name = "client"
    _inherit = "owner"

    property_ids = fields.One2many('property', 'client_id')
