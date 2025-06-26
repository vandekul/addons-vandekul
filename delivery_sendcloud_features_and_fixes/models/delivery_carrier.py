import json

from odoo import models, fields, api, _
import logging
from operator import itemgetter
from itertools import groupby
from pprint import pprint
from odoo.exceptions import ValidationError
from odoo.tools import float_round
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _name =  "delivery.carrier"
    _inherit = ["delivery.carrier"]

    def available_carriers(self, partner):
        sendcloud_carriers = []
        order_id = self.env.context.get("sale_order_id")
        if not order_id:
            order_id = self.env.context.get("default_order_id")
        if (
                not order_id
                and self.env.context.get("active_model") == "choose.delivery.carrier"
        ):
            wizard = self.env["choose.delivery.carrier"].browse(
                self.env.context.get("active_id")
            )
            order_id = wizard.order_id.id

        order = self.env["sale.order"].browse(order_id)
        if order.sendcloud_order_weight < order.sendcloud_order_volumetric_weight:
            order.sendcloud_order_weight = order.sendcloud_order_volumetric_weight
        _logger.info("Available carriers order_id: %s weight: %s volumetric: %s\n",
                     order_id,order.sendcloud_order_weight, order.sendcloud_order_volumetric_weight)

        available_carriers = super().available_carriers(partner)
        return available_carriers

    @api.model
    def _sendcloud_create_update_shipping_methods(
        self, shipping_methods, company_id, is_return=False
    ):
        """ Sync all available shipping methods for a specific company,
         regardless of the sender address.
        :return:
        """
        _logger.info("_sendcloud_create_update_shipping_methods\n")
        product = self._get_sendcloud_product_delivery(company_id)

        # All shipping methods
        domain = [
            ("delivery_type", "=", "sendcloud"),
            ("company_id", "=", company_id),
            ("sendcloud_is_return", "=", is_return),
        ]
        all_shipping_methods = self.with_context(active_test=False).search(domain)

        # Existing records
        shipping_methods_list = [method.get("id") for method in shipping_methods]
        existing_shipping_methods = all_shipping_methods.filtered(
            lambda c: c.sendcloud_code in shipping_methods_list
        )

        # Existing shipping methods map (internal code -> existing shipping methods)
        existing_shipping_methods_map = {}
        for existing in existing_shipping_methods:
            if existing.sendcloud_code not in existing_shipping_methods_map:
                existing_shipping_methods_map[existing.sendcloud_code] = self.env[
                    "delivery.carrier"
                ]
            existing_shipping_methods_map[existing.sendcloud_code] |= existing

        # Disabled shipping methods
        disabled_shipping_methods = all_shipping_methods - existing_shipping_methods
        disabled_shipping_methods.write({"active": False})

        # Created shipping methods and related pricelist by countries
        new_shipping_methods_vals = []
        new_country_vals = []
        for method in shipping_methods:
            vals = self._prepare_sendcloud_shipping_method_from_response(method)
            vals["product_id"] = product.id
            vals["sendcloud_is_return"] = is_return
            if method.get("id") in existing_shipping_methods_map:
                existing_shipping_methods_map[method.get("id")].write(vals)
            else:
                vals["company_id"] = company_id
                new_shipping_methods_vals += [vals]
            for country in method.get("countries"):
                #_logger.info("country %s\n", country)
                new_country_vals.append(
                    {
                        "sendcloud_code": country.get("id"),
                        "iso_2": country.get("iso_2"),
                        "iso_3": country.get("iso_3"),
                        "from_iso_2": country.get("from_iso_2"),
                        "from_iso_3": country.get("from_iso_3"),
                        "price": country["price"] if country["price"] is not None or 0 else country["price_breakdown"][0]["value"],
                        "method_code": method.get("id"),
                        "sendcloud_is_return": is_return,
                        "company_id": company_id,
                    }
                )
        new_created_shipping_methods = self.create(new_shipping_methods_vals)
        with self.env.norecompute():
            self.sudo().env["sendcloud.shipping.method.country"].search(
                [
                    ("company_id", "=", company_id),
                    ("sendcloud_is_return", "=", is_return),
                ]
            ).unlink()
            self.sudo().env["sendcloud.shipping.method.country"].create(
                new_country_vals
            )

        # Updated shipping methods
        updated_shipping_methods = (
            existing_shipping_methods + new_created_shipping_methods
        )
        updated_shipping_methods._sendcloud_set_countries()
        updated_shipping_methods.write({"active": True})

        # Carriers
        self.sendcloud_update_carriers(updated_shipping_methods)
        return shipping_methods

    def _update_sendcloud_delivery_carrier(self, integration):
        _logger.info("FIXES; _update_sendcloud_delivery_carrier\n")
        self.ensure_one()
        new_country_vals = []
        internal_code = self.sendcloud_code
        params = {"sender_address": "all"}
        carrier = integration.get_shipping_method(internal_code, params)
        company_id = carrier.get("company_id")
        is_return = carrier.get("is_return")
        vals = super()._prepare_sendcloud_shipping_method_from_response(carrier)
        for country in carrier.get("countries"):
            _logger.info("country %s\n", country)
            new_country_vals.append(
                {
                    "sendcloud_code": country.get("id"),
                    "iso_2": country.get("iso_2"),
                    "iso_3": country.get("iso_3"),
                    "from_iso_2": country.get("from_iso_2"),
                    "from_iso_3": country.get("from_iso_3"),
                    "price": country["price"] if country["price"] is not None or 0 else country["price_breakdown"][0][
                        "value"],
                    "method_code": carrier.get("id"),
                    "sendcloud_is_return": is_return,
                    "company_id": company_id,
                }
            )

        self.write(vals)
        with self.env.norecompute():
            self.sudo().env["sendcloud.shipping.method.country"].search(
                [
                    ("company_id", "=", company_id),
                    ("sendcloud_is_return", "=", is_return),
                ]
            ).unlink()
            self.sudo().env["sendcloud.shipping.method.country"].write(
                new_country_vals
            )