import json

from odoo import models, fields, api, _
import logging
from odoo.exceptions import ValidationError
from odoo.tools import float_round
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _name =  "delivery.carrier"
    _inherit = ["delivery.carrier"]

    def available_carriers(self, partner):
        order_id = self.env.context.get("sale_order_id")
        if not order_id:
            order_id = self.env.context.get("default_order_id")
        order = self.env["sale.order"].browse(order_id)
        if order.sendcloud_order_weight < order.sendcloud_order_volumetric_weight:
            order.sendcloud_order_weight = order.sendcloud_order_volumetric_weight
        _logger.info("Available carriers order_id: %s weight: %s volumetric: %s\n",
                     order_id,order.sendcloud_order_weight, order.sendcloud_order_volumetric_weight)
        return super().available_carriers(partner)