# -*- coding: utf-8 -*-
{
    'name': "pronto",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_payment_group','crm','purchase','sale_crm','sale_order_type','stock','stock_voucher','stock_picking_invoice_link','purchase_ux'],


    # always loaded
    'data': [       
        # 'security/pronto_security.xml',
        'security/ir.model.access.csv',

        'views/company.xml',                
        'views/crm_lead_views.xml',
        # 'views/menuitems.xml',
        # 'views/purchase_order_views.xml',
        'views/report_payment_group.xml',
        'views/report_stockpicking.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/sale_tipo_cliente_views.xml',
        'views/stock_picking_views.xml',        
    ],
}
