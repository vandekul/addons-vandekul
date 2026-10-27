# Copyright 2024 Susanna Fort (https://github.com/vandekul)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Delivery Packlink PRO",
    "summary": "Delivery Carrier implementation for Packlink PRO using their API",
    "version": "18.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/vandekul/susanna",
    "author": "Susanna Fort",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["delivery","stock" ],
    "external_dependencies": {"python": ["unidecode"]},
    "data": ["views/delivery_carrier_view.xml",
             "views/stock_picking_views.xml",
             "views/sale_order_view.xml"],
}
