from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ShotSize(models.Model):
    _name = 'liquor_store.shot_size'
    _description = 'Shot Size'
    
    size = fields.Integer('Shot Size(mls)', required=True)
    unit_price = fields.Integer('Unit Price', required=True)
            
