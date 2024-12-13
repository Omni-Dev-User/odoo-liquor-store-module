from odoo import fields, models, api, exceptions, _

class SalesOrder(models.Model):
    _name = 'liquor_store.sales.order'
    _description = 'Sales Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_seq'
    
    DISCOUNT_SELECTION = [
        ('0', '0%'), ('10', '10%'), ('20', '20%'), ('30', '30%'), ('40', '40%'),
        ('50', '50%'), ('60', '60%'), ('70', '70%'), ('80', '80%'), ('90', '90%'), ('100', '100%')
    ]
        
    STATE_SELECTION = [
        ('quotation', 'Quotation'),
        ('quotation_sent', 'Quotation Sent'),
        ('sales_order', 'Sales Order'),
        ('done', 'Done'),
    ]


    name_seq = fields.Char(string='Order Reference', required=True, readonly=True, copy=False, index=True, default=lambda self: _('New'))
    customer_id = fields.Many2one('liquor_store.customer', string='Customer', required=True)
    order_line_ids = fields.One2many('liquor_store.sales.order.line', 'order_id', string='Order Lines')
    payment_ids = fields.One2many('liquor_store.payment.details', 'order_id', string='Payments')
    total_amount = fields.Float(string='Total Sale Amount', compute='_compute_total_amount', store=True)
    total_paid = fields.Float(string='Total Paid Amount', compute='_compute_total_paid', store=True)
    remaining_amount = fields.Float(string='Change', compute='_compute_remaining_amount', store=True)
    state = fields.Selection(STATE_SELECTION, string='Status', default='quotation', readonly=True)
    date = fields.Date('Date Sold', default=fields.Date.today())
    discount = fields.Selection(DISCOUNT_SELECTION, string='Discount', default='0')
    
    def unlink(self):
        for order in self:
            if order.state == 'done':
                raise exceptions.UserError("You cannot delete a sales order that is in the 'Done' state.")
            if order.order_line_ids or order.payment_ids:
                raise exceptions.UserError("You cannot delete a sales order with associated sales order lines or payment details.")
        return super(SalesOrder, self).unlink()

    @api.depends('order_line_ids.subtotal', 'discount')
    def _compute_total_amount(self):
        for order in self:
            total = sum(order.order_line_ids.mapped('subtotal'))
            discount_amount = total * (float(order.discount) / 100)  # Convert discount to float
            order.total_amount = total - discount_amount
            
    @api.depends('payment_ids.amount')
    def _compute_total_paid(self):
        for order in self:
            order.total_paid = sum(order.payment_ids.mapped('amount'))
    
    @api.depends('total_amount', 'total_paid')
    def _compute_remaining_amount(self):
        for order in self:
            order.remaining_amount = order.total_paid - order.total_amount
            
    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('liquor_store.sales.order.sequence')
        return super(SalesOrder, self).create(vals)

    def action_send_by_email(self):
        self.write({'state': 'quotation_sent'})

    def action_confirm(self):
        self.write({'state': 'sales_order'})

    def action_validate(self):
        self.write({'state': 'done'})
        for order in self:
            order.order_line_ids.mapped('bottle_id').write({'status': 'sold'})
            sold_bottles = order.order_line_ids.filtered(lambda line: line.bottle_id.status == 'sold').mapped('bottle_id')
            sold_bottles.write({'selling_date': order.date})  # Update selling date of sold bottles
            for line in order.order_line_ids:
                line.bottle_id.write({'selling_price': line.subtotal})  # Update selling price of the bottle to subtotal

        
    def action_return(self):
        self.write({'state': 'quotation'})
        returned_bottles = self.order_line_ids.mapped('bottle_id')
        returned_bottles.filtered(lambda bottle: bottle.status == 'sold').write({'selling_date': False})  # Clear selling date of returned bottles
        self.order_line_ids.mapped('bottle_id').write({'status': 'available'})
    
    def print_sales_order_report(self):
        report_action = self.env['ir.actions.report'].search([('report_name', '=', 'liquor_store.report_sales_orders')], limit=1)
        if report_action:
            return report_action.report_action(self)
        else:
            raise exceptions.UserError("Report action not found. Please make sure the report action exists.")


class SalesOrderLine(models.Model):
    _name = 'liquor_store.sales.order.line'
    _description = 'Sales Order Line'

    order_id = fields.Many2one('liquor_store.sales.order', string='Sales Order')
    bottle_id = fields.Many2one('liquor_store.bottle', string='Bottle', required=True)
    quantity = fields.Integer(string='Quantity', default=1)
    unit_price = fields.Float(string='Unit Price', compute='_compute_unit_price', store=True)
    brand = fields.Char(string='Brand', compute='_compute_brand', store=False)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    selling_date = fields.Date(related='order_id.date', string='Selling Date', store=True)


    @api.depends('quantity', 'unit_price', 'order_id.discount')
    def _compute_subtotal(self):
        for line in self:
            discount_amount = line.unit_price * (float(line.order_id.discount) / 100)
            line.subtotal = (line.unit_price - discount_amount) * line.quantity

            
    @api.depends('bottle_id')
    def _compute_unit_price(self):
        for line in self:
            line.unit_price = line.bottle_id.selling_price
            
    @api.depends('bottle_id')
    def _compute_brand(self):
        for line in self:
            line.brand = line.bottle_id.brand.name
            
    @api.constrains('bottle_id', 'order_id')
    def _check_unique_bottle_id(self):
        for line in self:
            if line.order_id and line.bottle_id:
                existing_line = self.env['liquor_store.sales.order.line'].search([
                    ('order_id', '=', line.order_id.id),
                    ('bottle_id', '=', line.bottle_id.id),
                    ('id', '!=', line.id),
                ])
                if existing_line:
                    raise exceptions.ValidationError(
                        "You cannot add the same bottle to the order multiple times."
                    )
                    
class PaymentDetails(models.Model):
    _name = 'liquor_store.payment.details'
    _description = 'Payment Details'
    
    PAYMENT_TYPE_SELECTION = [
        ('bank', 'Bank'),
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money')
    ]

    order_id = fields.Many2one('liquor_store.sales.order', string='Sales Order')
    payment_type = fields.Selection(PAYMENT_TYPE_SELECTION, string='Payment Type')
    amount = fields.Float(string='Amount')
    date = fields.Date(string='Selling Date', compute='_compute_selling_date', store=True)

    @api.depends('order_id.date')
    def _compute_selling_date(self):
        for payment in self:
            payment.date = payment.order_id.date 
            
    @api.depends('order_id.state', 'amount')
    def _compute_done_state_amount(self):
        for payment in self:
            if payment.order_id.state == 'done':
                payment.done_state_amount = payment.amount
            else:
                payment.done_state_amount = 0.0

    done_state_amount = fields.Float(string='Amount in Done State', compute='_compute_done_state_amount', store=True)

class Invoice(models.Model):
    _name = 'liquor_store.invoice'
    _description = 'Invoice'

    customer_id = fields.Many2one('liquor_store.customer', string='Customer', required=True)
    invoice_line_ids = fields.One2many('liquor_store.invoice_line', 'invoice_id', string='Invoice Lines')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    tax = fields.Float(string='Tax', required=True, default=0.0)
    total_amount_due = fields.Float(string='Total Amount Due', compute='_compute_total_amount_due', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
    ], string='Status', default='draft', readonly=True)

    @api.depends('invoice_line_ids.subtotal')
    def _compute_subtotal(self):
        for invoice in self:
            invoice.subtotal = sum(invoice.invoice_line_ids.mapped('subtotal'))

    @api.depends('subtotal', 'tax')
    def _compute_total_amount_due(self):
        for invoice in self:
            invoice.total_amount_due = invoice.subtotal + invoice.tax
            
    def action_confirm_invoice(self):
        self.write({'state': 'posted'})


class InvoiceLine(models.Model):
    _name = 'liquor_store.invoice_line'
    _description = 'Invoice Line'

    invoice_id = fields.Many2one('liquor_store.invoice', string='Invoice')
    bottle_id = fields.Many2one('liquor_store.bottle', string='Bottle', required=True)
    quantity = fields.Integer(string='Quantity', default=1)
    unit_price = fields.Float(string='Unit Price', required=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
