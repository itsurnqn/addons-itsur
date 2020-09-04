# Copyright 2020 ITSur - Juan Pablo Garza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "delivery_qx",
    "version": "12.0.1.0.0",
    "author": "ITSur",
    "website": "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list    
    "category": "Uncategorized",
    
    "license": "AGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["juanpgarza"],
    "depends": ['delivery','base_location'],
    
    "data": [
        # 'security/ir.model.access.csv',
        'views/delivery_qx_view.xml',
        'views/res_city_views.xml',
        'views/templates.xml',
        'security/ir.model.access.csv',
        'data/zona_qx_data.xml',
    ],
    'installable': True,
}