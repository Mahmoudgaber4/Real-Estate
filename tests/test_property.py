from odoo.tests.common import TransactionCase
from odoo import fields

class TestProperty(TransactionCase):


    # over ride (setup method), and create test record (all fields of model)
    def setUp(self, *args, **kwargs):
        super(TestProperty, self).setUp()

        self.property_01_record = self.env['property'].create({
            'ref': 'PRT1000',
            'name': 'property 1000',
            'description': 'property 1000 description',
            'postcode': '1001',
            'availability_date': fields.Date.today(),
            'bedrooms': 10,
            'expected_price': 400000,
        })

    # Handle test method (check value or type of fields or another logic)
    def test_01_property_values(self):
        # use created record
        property_id = self.property_01_record
        # method to check values (created_record, dic of values)
        # compare value of created record with values
        self.assertRecordValues(property_id, [{
            'ref': 'PRT1000',
            'name': 'property 1000',
            'description': 'property 1000 description',
            'postcode': '1001',
            'availability_date': fields.Date.today(),
            'bedrooms': 10,
            'expected_price': 400000,
        }])
