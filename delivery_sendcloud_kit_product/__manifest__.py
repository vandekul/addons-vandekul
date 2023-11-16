# Copyright 2023 Vandekul (<https://github.com/vandekul>)
# License OPL-1 (https://www.odoo.com/documentation/16.0/legal/licenses.html#odoo-apps).

{
    "name": "Sendcloud Shipping Sending KIT products",
    "summary": "Compute shipping costs and ship with Sendcloud",
    "images": ["static/description/logo-home.jpg"],
    "category": "Operations/Inventory/Delivery",
    "version": "16.0",
    "author": "Vande",
    "license": "OPL-1",
    "depends": ["delivery_sendcloud_official"],
    "data": ["security/ir.model.access.csv",
             "views/sendcloud_integration_view.xml"],
}
