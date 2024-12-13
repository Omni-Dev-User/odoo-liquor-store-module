from odoo import fields, models, api
from odoo.exceptions import UserError

class Bottle(models.Model):
    _name = 'liquor_store.bottle'
    _description = 'Bottle'
    _rec_name = 'barcode_number'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    brand = fields.Many2one('liquor_store.brand', 'Brand', required=True, tracking=True)
    barcode_number = fields.Char('Barcode Number', tracking=True, required=True)
    size = fields.Many2one('liquor_store.bottle_size','Select Capacity (mls)', required=True,)


    capacity = fields.Integer(string='Capacity (mls)', compute="_compute_remaining_capacity", store=True)
    purchase_date = fields.Date('Purchase Date', default=fields.Date.today(), required=True)
    selling_date = fields.Date('Selling Date')
    purchase_cost = fields.Integer('Purchase Cost', required=True)
    selling_price = fields.Integer('Selling Price', required=True,)
    status = fields.Selection(string='Status', selection=[('available', 'Available'), ('sold', 'Sold')], default='available', tracking=True, required=True,)
    variants = fields.Many2many('liquor_store.bottle_variant', string='Variants')
                
    @api.model
    def create(self, vals):
        if 'size' not in vals or not vals['size']:
            raise UserError("Size is required.")
        if 'purchase_cost' in vals and vals['purchase_cost'] <= 0:
            raise UserError("Purchase cost must be greater than zero.")
        if 'selling_price' in vals and vals['selling_price'] <= 0:
            raise UserError("Selling price must be greater than zero.")
        bottle = super(Bottle, self).create(vals)
        bottle.brand.quantity += 1
        return bottle
    
    def write(self, vals):
        if 'size' in vals and not vals['size']:
            raise UserError("Size is required.")
        if 'purchase_cost' in vals and vals['purchase_cost'] <= 0:
            raise UserError("Purchase cost must be greater than zero.")
        if 'selling_price' in vals and vals['selling_price'] <= 0:
            raise UserError("Selling price must be greater than zero.")
        return super(Bottle, self).write(vals)
    
    @api.depends('status')
    def _compute_selling_date(self):
        for bottle in self:
            if bottle.status == 'sold':
                # Find the related sales order line and get its sales order's date
                sale_order_line = self.env['liquor_store.sales.order.line'].search([('bottle_id', '=', bottle.id)], limit=1)
                if sale_order_line:
                    bottle.selling_date = sale_order_line.order_id.date
                else:
                    bottle.selling_date = False
            else:
                bottle.selling_date = False
    
    @api.depends('size')
    def _compute_remaining_capacity(self):
        for bottle in self:
            bottle.capacity = bottle.size.size

    def unlink(self):
        for bottle in self:
            if bottle.brand:
                bottle.brand.quantity -= 1
        return super(Bottle, self).unlink()

    def sell_bottle(self):
        if self.capacity == self.size.size:
            self.status = 'sold'
            self.brand.quantity -= 1
            return True
        else:
            raise UserError("Cannot sell the entire bottle unless it's at full capacity.")
            
    def name_get(self):
        result = []
        for bottle in self:
            name = "%s - %s" % (bottle.brand.name, bottle.barcode_number)
            result.append((bottle.id, name))
        return result
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = ['|', ('barcode_number', operator, name), ('brand.name', operator, name)]
        bottles = self.search(domain + args, limit=limit)
        return bottles.name_get()
    
    _sql_constraints = [
        ('barcode_number_unique', 'UNIQUE (barcode_number)', 'Barcode number must be unique.'),
    ]
        