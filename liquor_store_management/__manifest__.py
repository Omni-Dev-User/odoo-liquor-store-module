
{
    'name': 'Odoo Liquor Store Management System',
    'depends' : ['mail', 'base', 'web', 'sale', 'board'],
    'author': 'Omni Software Ltd',
    'sequence': 1,
    'summary': 'Comprehensive Management System for Liquor Stores',
    'description': """
    Odoo 17 Community Edition Liquor Store Management System

    Features:
    - Brand Management
    - Bottle Inventory Tracking
    - Customer Management
    - Supplier Transactions
    - Sales Order Processing
    - Invoicing
    - Reporting and Analytics
    - Sales Dashboard
    """,
    'website': 'https://omnitech.co.ug/',
    'data': [
        'security/access_groups.xml',
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/sequence_data.xml',
        'views/liquor_store_brand.xml',
        'views/liquor_store_bottles.xml',
        'views/liquor_store_bottle_size.xml',
        'views/liquor_store_customer.xml',
        'views/liquor_store_supplier.xml',
        'views/liquor_store_rfq.xml',
        'views/liquor_store_invoices.xml',
        'views/liquor_store_sales.xml',
        'views/liquor_store_sales_order_reporting.xml',
        'views/liquor_store_sales_analysis.xml',
        'views/liquor_store_sales_payment_type_analysis.xml',
        'views/liquor_store_supplier_transaction.xml',
        'views/sales_dashboard.xml',
        'views/liquor_store_menus.xml',
        'reports/sales_orders_report_template.xml',
        'reports/report.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
    'installable': True,
    'assets': {
        'web.assets_backend': [
            'liquor_store_management/static/src/components/**/*.js',
            'liquor_store_management/static/src/components/**/*.xml',
            'liquor_store_management/static/src/components/**/*.scss',
            'liquor_store_management/static/src/**/*',
        ],
    },
    'images': ['static/description/banner.jpg'],
}