# -*- coding: utf-8 -*-
{
    'name': "box",

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
    'depends': ['base','account','account_payment_group','account_payment_credit_card_mgmt'],

    # always loaded
    'data': [
        'security/box_security.xml',
        'security/ir.model.access.csv',
        'wizard/box_session_cash.xml',
        'views/box_box_views.xml',        
        'views/box_session_views.xml',
        'views/box_session_journal_views.xml',
        'views/box_session_journal_line_views.xml',
        'views/menus.xml',
        'views/templates.xml',
        'views/account_payment_group_views.xml',        
        'views/account_payment_views.xml',
        'views/res_users_views.xml',        
    ],
}