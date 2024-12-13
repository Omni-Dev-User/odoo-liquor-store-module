from odoo import fields, models, api, _
from odoo.exceptions import UserError

class Shot(models.Model):
    _name = 'liquor_store.shot'
    _description = 'Shot'
    
    bottle = fields.Many2one('liquor_store.bottle', 'Bottle', required=True)
    bottle_brand = fields.Char(compute='_compute_bottle_brand')
    size = fields.Integer('Shot Size', required=True)
    unit_price = fields.Integer('Unit Price', required=True)
    quantity = fields.Integer('Quantity', required=True)
    bottle_barcode_number = fields.Char(related='bottle.barcode_number', string='Bottle Barcode Number', readonly=True)
    
    @api.depends('bottle')
    def _compute_bottle_brand(self):
        for record in self:
            record.bottle_brand = record.bottle.brand.name
            
    @api.model
    def create(self, vals):
        shot = super(Shot, self).create(vals)        
        total_amount = shot.size * shot.quantity
        print(shot.quantity)
        print(shot.size)
        print(shot.bottle.capacity)  
        print(total_amount)      
        if shot.bottle:
            print(shot.bottle.capacity >= total_amount)
            if shot.bottle.capacity >= total_amount:
                shot.bottle.capacity -= total_amount
                shot.bottle.selling_price += (shot.quantity * shot.unit_price)
                if shot.bottle.capacity == 0:
                    shot.bottle.status = 'sold'
                return shot
            else:
                raise UserError("Total shots to sell are greater than remaining capacity.")
        

    def unlink(self):
        for shot in self:
            if shot.bottle and shot.bottle.status == 'sold':
                raise UserError(_("Cannot delete a shot from a sold bottle."))
            else:
                total_amount = shot.size * shot.quantity
                shot.bottle.capacity += total_amount
                shot.bottle.selling_price -= (shot.quantity * shot.unit_price)
                return super(Shot, self).unlink()
            
