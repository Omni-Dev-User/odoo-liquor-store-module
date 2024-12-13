from odoo import fields, models, api
from odoo.exceptions import UserError

class Payment(models.Model):
    _name = 'liquor_store.payment'
    _description = 'Payment'

    journal = fields.Selection([
        ('bank', 'Bank'),
        ('cash', 'Cash'),
    ], string='Payment Method', default='cash')
    payment_method = fields.Selection([
        ('manual', 'Manual'),
        ('online', 'Online'),
    ], string='Payment Method', default='manual')
    amount = fields.Float(string='Amount', required=True)
    recipient_bank_account = fields.Char(string='Recipient Bank Account')
    payment_date = fields.Date(string='Payment Date', default=fields.Date.today)
    memo = fields.Char(string='Memo')

    def action_create_payment(self):
        # Your payment creation logic goes here
        pass

    def action_discard(self):
        # Your discard logic goes here
        special="cancel"
        pass
