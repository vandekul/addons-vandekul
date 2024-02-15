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

    def _get_delivery_methods(self):
        # Modify the shipping methods so that it takes into account only those that meet the weight of the order
        available_carriers = super()._get_delivery_methods()
        sendcloud_carriers = available_carriers.filtered(
            lambda c: c.delivery_type == "sendcloud" and c.sendcloud_is_return is False
        )
        order = self.env["sale.order"].browse(self.env.context.get("sale_order_id"))
        weight = order.sendcloud_order_weight
        sendcloud_carriers = sendcloud_carriers.filtered(
            lambda c: c.sendcloud_min_weight <= weight <= c.sendcloud_max_weight
        )

        other_carriers = available_carriers.filtered(lambda c: c.delivery_type != "sendcloud")

        #for delivery in (sendcloud_carriers + other_carriers):
            #_logger.info("DELIVERY: %s\n", delivery.name)
        return sendcloud_carriers + other_carriers