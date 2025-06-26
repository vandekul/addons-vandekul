# Copyright 2023 Vandekul (<https://github.com/vandekul>)
# License OPL-1 (https://www.odoo.com/documentation/16.0/legal/licenses.html#odoo-apps).

from collections import defaultdict
import logging
import json
import uuid
import pprint

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order"]

    sendcloud_order_volumetric_weight = fields.Float(compute="_compute_sendcloud_order_volumetric_weight")

    def _get_delivery_methods(self):
        # Modify the shipping methods so that it takes into account only those that meet the weight of the order
        weight = 0
        resultat = []
        available_carriers = super()._get_delivery_methods()
        sendcloud_carriers = available_carriers.filtered(
            lambda c: c.delivery_type == "sendcloud" and c.sendcloud_is_return is False
        )
        order = self.env["sale.order"].browse(self.env.context.get("sale_order_id"))

        if order.sendcloud_order_weight > order.sendcloud_order_volumetric_weight:
            weight = order.sendcloud_order_weight
        else:
            weight = order.sendcloud_order_volumetric_weight
        sendcloud_carriers = sendcloud_carriers.filtered(
            lambda c: c.sendcloud_min_weight <= weight <= c.sendcloud_max_weight
        )

        other_carriers = available_carriers.filtered(lambda c: c.delivery_type != "sendcloud")
        resultat_total = sendcloud_carriers + other_carriers

        # Ordenamos los métodos de envío de más barato a más caro
        def get_dc_price(dc):
            res = dc.rate_shipment(order)
            return res['price']

        resultat = resultat_total.sorted(key=get_dc_price)
        number_of_carriers = self.sudo().carrier_id.sendcloud_integration_id.number_of_carriers
        if number_of_carriers <= 0:
            return resultat
        else:
            return resultat[:number_of_carriers]

    def _cart_update(self, *args, **kwargs):
        """ Override to update carrier quotation if quantity changed """
        # TODO
        # product_id, line_id=None, add_qty=0, set_qty=0
        return super()._cart_update(*args, **kwargs)


    @api.depends(
        "order_line.product_id.weight",
        "order_line.product_qty",
        "order_line.display_type",
    )
    def _compute_sendcloud_order_volumetric_weight(self):
        volumetric_weight = 0
        for order in self:

            for line in order.order_line:
                if line.product_id.detailed_type == 'product':
                    if line.product_id.product_height > 0 and line.product_id.product_width > 0 and line.product_id.product_length > 0:
                        volumetric_weight += ((line.product_id.product_height * line.product_id.product_width * line.product_id.product_length)/5000)* line.product_qty
                    #_logger.info("Line %s %s x %s x %s = %s\n", line.product_id.name, line.product_id.product_height,
                    #             line.product_id.product_width, line.product_id.product_length, volumetric_weight)
                #_logger.info("Heigh x lenght x width = %s\n", volumetric_weight)

            order.sendcloud_order_volumetric_weight = round(volumetric_weight,2)