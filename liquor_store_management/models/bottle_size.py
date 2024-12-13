from odoo import fields, models, api, _

class BottleSize(models.Model):
    _name = 'liquor_store.bottle_size'
    _description = 'Bottle Size'
    _rec_name = 'size'
    
    size = fields.Integer('Bottle Size(mls)', required=True, default=750, unique=True)

