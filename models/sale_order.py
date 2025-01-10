from odoo import models, fields

class SaleOrde(models.Model):
    _inherit = 'sale.order'

    property_id = fields.Many2one('property', string='Property Name')
    property_selling_price = fields.Float(related='property_id.selling_price', string="Property Selling Price")
