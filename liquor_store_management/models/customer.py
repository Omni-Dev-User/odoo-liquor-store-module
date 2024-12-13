from odoo import fields, models

class Customer(models.Model):
    _name = 'liquor_store.customer'
    _description = 'Customer'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    address = fields.Text(string='Address', required=True)
