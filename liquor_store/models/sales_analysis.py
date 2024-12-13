from odoo import models, fields, api, tools

class SalesAnalysisReport(models.Model):
    _name = 'liquor_store.sales.analysis'
    _description = 'Sales Analysis Report'
    _auto = False

    brand_id = fields.Many2one('liquor_store.brand', string='Brand', readonly=True)
    total_sales_amount = fields.Float(string='Total Sales Amount', readonly=True)
    quantity_sold = fields.Integer(string='Quantity Sold', readonly=True)
    total_profit = fields.Float(string='Total Profit', readonly=True)    
    selling_date = fields.Date('Selling Date', readonly=True)


    # Add id field explicitly to avoid the UndefinedColumn error
    id = fields.Integer(string='ID', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    ROW_NUMBER() OVER () as id,
                    b.id AS brand_id,
                    b.name AS brand_name,
                    sol.selling_date,
                    SUM(sol.subtotal) AS total_sales_amount,
                    SUM(sol.quantity) AS quantity_sold,
                    SUM((sol.quantity * (btl.selling_price - btl.purchase_cost))) AS total_profit
                FROM
                    liquor_store_sales_order_line sol
                JOIN
                    liquor_store_bottle btl ON sol.bottle_id = btl.id
                JOIN
                    liquor_store_brand b ON btl.brand = b.id
                JOIN
                    liquor_store_sales_order so ON sol.order_id = so.id
                WHERE
                    so.state = 'done'
                GROUP BY
                    b.id, b.name, sol.selling_date
            )
        """ % (self._table,))



    # Method to get the most selling brand
    def get_most_selling_brand(self, start_date=None, end_date=None):
        domain = [('start_date', '>=', start_date), ('end_date', '<=', end_date)] if start_date and end_date else []
        most_selling_brand = self.env['liquor_store.sales.analysis'].search(domain, order='quantity_sold DESC', limit=1)
        return most_selling_brand
