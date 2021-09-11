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
    'depends': ['base','account_payment_group','crm','purchase','sale_crm',
                'sale_order_type','stock','stock_voucher','stock_picking_invoice_link','purchase_ux',
                'sale_stock_info_popup','sale_ux','product_pack','delivery','sale_stock_ux','stock_ux','account_financial_risk','product'],

    # always loaded
    'data': [
        'views/report_deliveryslip.xml',
        'views/stock_quant_views.xml',        
        'security/pronto_security.xml',
        'wizards/partner_risk_exceeded_view.xml',        
        'views/stock_return_picking_reason_views.xml',
        'wizards/stock_return_picking_views.xml',
        'views/product_pricelist_item_history_views.xml',
        'views/project_task_views.xml',
        'views/product_price_history_views.xml',
        'views/mail_activity_view.xml',               
        'report/sale_report_pronto.xml',        
        'views/sale_views.xml',        
        'security/ir.model.access.csv',
        'views/account_check_views.xml',
        'views/account_payment_views.xml',
        'views/company.xml',                
        'views/crm_lead_views.xml',
        # 'views/menuitems.xml',
        # 'views/purchase_order_views.xml',
        # 'views/report_payment_group.xml',
        'views/report_stockpicking.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/sale_tipo_cliente_views.xml',
        'views/stock_picking_views.xml',
        'views/product_pricelist_item_views.xml',
        'views/product_template_views.xml',
        'views/res_users_views.xml',  
        'views/account_payment_group_views.xml',
        'views/stock_inventory_views.xml',
        'wizards/update_price_views.xml',
        'data/product_stock_data.xml',
        'data/config_parameter.xml',
        'views/sale_portal_templates.xml',
        'views/stock_location_views.xml',
        'views/report_stockpicking_operations.xml',        
        'data/pronto_data.xml',        
    ],
}
