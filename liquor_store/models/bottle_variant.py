from odoo import fields, models, api, _

class BottleVariant(models.Model):
    _name = 'liquor_store.bottle_variant'
    _description = 'Bottle Variant'
    _rec_name = 'name'
    
    name = fields.Char('Variant Name', required=True)
    bottle_id = fields.Many2one('liquor_store.bottle', 'Bottle Template', required=True)

