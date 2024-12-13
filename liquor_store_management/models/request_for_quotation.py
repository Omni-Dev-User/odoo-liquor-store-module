from odoo import fields, models, api

class RequestForQuotation(models.Model):
    _name = 'liquor_store.rfq'
    _description = 'Request for Quotation'

    customer_id = fields.Many2one('liquor_store.customer', string='Customer', required=True)
    rfq_line_ids = fields.One2many('liquor_store.rfq_line', 'rfq_id', string='RFQ Lines')
    total_amount = fields.Float(string='Total RFQ Amount', compute='_compute_total_amount', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
        ], string='Status', default='draft', readonly=True)
    
    invoice_id = fields.Many2one('liquor_store.invoice', string='Invoice', readonly=True, copy=False)

    @api.depends('rfq_line_ids.subtotal')
    def _compute_total_amount(self):
        for rfq in self:
            rfq.total_amount = sum(rfq.rfq_line_ids.mapped('subtotal'))

    def action_send_rfq(self):
        self.write({'state': 'sent'})

    def action_accept_rfq(self):
        self.write({'state': 'accepted'})

    def action_reject_rfq(self):
        self.write({'state': 'rejected'})
        
    def action_create_invoice(self):
        invoice_vals = {
            'customer_id': self.customer_id.id,
            'invoice_line_ids': [(0, 0, {
                'bottle_id': line.bottle_id.id,
                'quantity': line.quantity,
                'unit_price': line.unit_price,
            }) for line in self.rfq_line_ids],
        }
        invoice = self.env['liquor_store.invoice'].create(invoice_vals)
        self.write({'invoice_id': invoice.id})
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'liquor_store.invoice',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

class RFQLine(models.Model):
    _name = 'liquor_store.rfq_line'
    _description = 'RFQ Line'

    rfq_id = fields.Many2one('liquor_store.rfq', string='RFQ')
    bottle_id = fields.Many2one('liquor_store.bottle', string='Bottle', required=True)
    quantity = fields.Integer(string='Quantity', default=1)
    unit_price = fields.Float(string='Expected Unit Price', compute='_compute_unit_price', store=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
            
    @api.depends('bottle_id')
    def _compute_unit_price(self):
        for line in self:
            line.unit_price = line.bottle_id.selling_price
