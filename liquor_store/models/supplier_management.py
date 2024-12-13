from odoo import fields, models

class Supplier(models.Model):
    _name = 'liquor_store.supplier'
    _description = 'Supplier'
    
    name = fields.Char('Supplier Name')
    phone_number = fields.Char('Phone Number')
    email = fields.Char('Email')
    address = fields.Char('Location')
    
class SupplierTransaction(models.Model):
    _name = 'liquor_store.supplier_transaction'
    _description = 'Supplier Transaction'
    
    supplier = fields.Many2one('liquor_store.supplier', 'Supplier', required=True)
    brand = fields.Char('Brand', required=True)
    order_date = fields.Datetime('Order Date', default=fields.Datetime.now, required=True)
    delivery_date = fields.Datetime('Delivery Date')
    unit_price = fields.Float('Unit Price', required=True)
    amount = fields.Float('Amount', required=True)
    date_received = fields.Date('Date Received')
    status = fields.Selection([('new', 'New'), ('pending', 'Pending'), ('completed', 'Completed')], 'Status', required=True, default='new')
    user_id = user_id = fields.Many2one('res.users', string="Admin", default=lambda self: self.env.user)
            
    def action_cancel(self):
        for record in self:
            record.status = "new"
            
    def action_send_mail(self):
        template = self.env.ref('liquor_store.liquor_store_supplier_transaction_email_template')
        for record in self:
            record.status = "pending"
            template.send_mail(record.id, force_send=True)
    