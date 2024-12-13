from odoo import fields, models, api

class Brand(models.Model):
    _name = 'liquor_store.brand'
    _description = 'Brand'
    _rec_name = 'name'
    
    name = fields.Char('Brand Name', required=True)
    description = fields.Text('Description', required=True)
    quantity = fields.Integer('In Stock', compute='_compute_quantity')
    bottle_ids = fields.One2many('liquor_store.bottle', 'brand', string='Bottles')
    sold_bottle_count = fields.Integer('Sold Bottle Count', compute='_compute_sold_bottle_count')
    total_profit = fields.Float('Total Profit', compute='_compute_total_profit')

    @api.depends('bottle_ids.purchase_cost', 'bottle_ids.selling_price', 'bottle_ids.status')
    def _compute_total_profit(self):
        for brand in self:
            total_profit = 0.0
            for bottle in brand.bottle_ids.filtered(lambda b: b.status == 'sold'):
                total_profit += bottle.selling_price - bottle.purchase_cost
            brand.total_profit = total_profit

    @api.depends('bottle_ids.status')
    def _compute_quantity(self):
        for brand in self:
            available_bottles = brand.bottle_ids.filtered(lambda b: b.status == 'available')
            brand.quantity = len(available_bottles)
            if not available_bottles:
                brand.quantity = 0
                
    @api.depends('bottle_ids.status')
    def _compute_sold_bottle_count(self):
        for brand in self:
            sold_bottles = brand.bottle_ids.filtered(lambda b: b.status == 'sold')
            brand.sold_bottle_count = len(sold_bottles)
