# Copyright 2020 ITSur - Juan Pablo Garza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "pronto_website_sale",
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
    "depends": [
        'website_sale',
        'l10n_ar_partner',
    ],
    
    "data": [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    'installable': True,
}