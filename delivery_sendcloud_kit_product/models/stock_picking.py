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


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking"]

    def _prepare_sendcloud_vals_from_picking(self, package=False):
        vals = super()._prepare_sendcloud_vals_from_picking(package=package)

        kit_product = self.sudo().carrier_id.sendcloud_integration_id.kit_product
        _logger.info("Prepare_sendcloud_vals_from_picking %s", kit_product)
        if kit_product:
            move_lines = self.move_ids.mapped("move_line_ids")
            if package:
                move_lines = move_lines.filtered(lambda l: l.package_id == package or l.result_package_id == package)
            else:
                move_lines = move_lines.filtered(lambda l: not l.package_id and not l.result_package_id)
            if move_lines:
                moves = move_lines.mapped("move_id")
            else:
                moves = self.move_ids  # TODO should be never the case, raise an error?
            parcel_items = []
            total_weight = 0.0
            kit_description = ""
            for move in moves:
                # If we want to send only KIT product and not all sub-products
                if move.sale_line_id.product_id.is_kits:
                    if kit_description != move.sale_line_id.product_id.display_name and kit_product:
                        line_vals = self._prepare_sendcloud_item_vals_from_kit(move, package=package)
                        kit_description = line_vals["description"]
                        total_weight += line_vals["weight"]
                        parcel_items += [line_vals]
            vals["parcel_items"] = parcel_items

        return vals

    def _prepare_sendcloud_item_vals_from_moves(self, move, package=False):
        line_vals = super()._prepare_sendcloud_item_vals_from_moves(move=move, package=package)

        weight = self._sendcloud_convert_weight_to_kg(move.product_id.weight)
        # Modify how to calc price from BOM (1/2)
        if move.sale_line_id.purchase_price != 0:
            price = round(
                ((move.product_id.standard_price / move.sale_line_id.purchase_price) * move.sale_line_id.price_unit), 2)
        else:
            price = round(move.sale_line_id.price_unit, 2)

        description = move.product_id.display_name

        line_vals.update(
            {"weight": weight,
             "description": description,
             "value": price
             }
        )
        return line_vals

    def _prepare_sendcloud_item_vals_from_kit(self, move, package=False):
        self.ensure_one()

        #_logger.info("KIT %s %s", move.sale_line_id.product_id.is_kits, move.product_id)
        # Modify weight to get from product_id
        weight = self._sendcloud_convert_weight_to_kg(move.sale_line_id.product_id.weight)

        quantity = int(move.product_uom_qty)  # TODO should be quantity_done ?
        partner_country = self.partner_id.country_id.code
        is_outside_eu = not self.partner_id.sendcloud_is_in_eu

        partner_state = self.partner_id.state_id.code
        state_requires_hs_code = self._check_state_requires_hs_code(partner_country, partner_state)
        price = round(move.sale_line_id.price_unit,2)
        description = move.sale_line_id.product_id.display_name


        # Parcel items (mandatory)
        line_vals = {
            "description": description,
            "quantity": quantity,
            "weight": (weight*quantity),
            # Modify how to calc price from BOM (2/2)
            "value": price,
            # not converted to euro as the currency is always set
        }
        #_logger.info("\nSENDCLOUD ITEM: Descr %s - Quanty %f - Weight %f - Price %f", move.product_id.display_name, quantity, weight, price)
        # Parcel items (mandatory when shipping outside of EU)
        if is_outside_eu or state_requires_hs_code:
            parcel_item_outside_eu = self._prepare_sendcloud_parcel_items_outside_eu(move)
            if not parcel_item_outside_eu.get("hs_code"):
                raise ValidationError(
                    _(
                        "Harmonized System Code is mandatory when shipping outside of EU and to some states.\n"
                        "You should set the HS Code for product %s"
                    )
                    % move.sale_line_id.product_tmpl_id.name
                )
            if not parcel_item_outside_eu.get("origin_country"):
                raise ValidationError(
                    _("Origin Country is mandatory when shipping outside of EU and to some states.")
                )
            line_vals.update(parcel_item_outside_eu)
        # Parcel items (optional)
        if move.sale_line_id.product_id.default_code:
            line_vals.update(
                {"sku": move.sale_line_id.product_id.default_code}
            )  # TODO product.barcode or product.id
        line_vals.update(
            {
                "product_id": ""
                # TODO product_id: product_code, the internal ID of the product. Is there a way to retrieve product (internal_code) from Sendcloud?
            }
        )
        line_vals.update(
            {
                "properties": {}
                # TODO The list of properties of the product. Used as a JSON object with {‘key’: ‘value’}
            }
        )
        _logger.info("KIT %s", pprint.pformat(line_vals))
        return line_vals