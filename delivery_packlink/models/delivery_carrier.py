# Copyright 2021 Studio73 - Ethan Hildick <ethan@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import logging
_logger = logging.getLogger(__name__)

from odoo import _, fields, models

from .packlink_pro_request import (
    PACKLINK_PRO_LABEL_TYPE,
    PACKLINK_PRO_SHIPMENT_TYPE,
    PacklinkProRequest,
)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    draft = fields.Boolean("Crear Borrador ", default=True)
    default_shipment_type = fields.Selection(selection=PACKLINK_PRO_SHIPMENT_TYPE)
    package_kit_length = fields.Float("Package KIT Length", default=30.0)
    package_kit_height = fields.Float("Package KIT Height", default=27.0)
    package_kit_width = fields.Float("Package KIT Width", default=14.0)

    envelope_length = fields.Float("Envelope Length", default=27.0)
    envelope_height = fields.Float("Envelope Height", default=24.0)
    envelope_width = fields.Float("Envelope Width", default=3.0)

    package_coeficient = fields.Float("Coeficient", default=5000)

    dropoff = fields.Boolean("Punt d'entrega (dropoff) ", default = False)
    delivery_to_parcelshop = fields.Boolean("Punt de recollida (parcelshop)", default = False)


    delivery_type = fields.Selection(
        selection_add=[("packlink_pro", "Packlink PRO")],
        ondelete={"packlink_pro": "set default"},
    )
    packlink_pro_api = fields.Char()
    packlink_pro_label_type = fields.Selection(
        string="Packlink PRO Label type", selection=PACKLINK_PRO_LABEL_TYPE
    )

    def _get_order_type(self, order):
        type = "envelope"
        for product in order.order_line:
            if product.product_id.is_kits:
                return "kit"
            elif product.product_id.product_height:
                type = "stacked"
        return type

    def _prepare_order_package(self, order):
        # type: kit, stacked, envelope
        length = 0.0
        height = 0.0
        width = 0.0
        weight = 0.0
        type = self._get_order_type(order)
        _logger.info("TYPE: %s\n", type)
        if type == "kit":
            length = self.package_kit_length
            height = self.package_kit_height
            width = self.package_kit_width
            weight = (length * height * width) / self.package_coeficient
        elif type == "stacked":
            is_accessories = False
            for product in order.order_line:
                if product.product_id.product_height and product.product_id.detailed_type == 'product':
                    length = self.package_kit_length
                    width = self.package_kit_width
                    height += product.product_id.product_height
                    weight += product.product_id.weight
                elif not product.product_id.product_height and product.product_id.detailed_type == 'product':
                    # Afegim la caixa d'accessoris
                    if not is_accessories:
                        height += 5.0
                        weight += product.product_id.weight
                        is_accessories = True
                    # Ja tenim caixa d'accessoris només sumem el pes
                    else:
                        weight += product.product_id.weight

            weight = max(weight, (length * height * width) / self.package_coeficient)
        elif type == "envelope":
            for product in order.order_line:
                weight += product.product_id.weight
            length = self.envelope_length
            height = self.envelope_height
            width = self.envelope_width
            weight = max(weight, (length * height * width) / self.package_coeficient)
        return (length, height, width, weight)


    def _prepare_packlink_pro_order(self, order):
        length, height, width, weight = self._prepare_order_package(order)
        _logger.info("Package (length x height x width) %f x %f x %f - Weight %f\n", length, height, width, weight)
        vals ={
            'from':
                {
                    'country': self.env.company.country_id.code,
                    'zip': self.env.company.zip
                },
            'packages': [
                 {
                     'length': length,
                     'height': height,
                     'width': width,
                     'weight': weight
                 }
            ],
            'to':
                {
                    'country': order.partner_shipping_id.country_id.code,
                    'zip': order.partner_shipping_id.zip
                }
        }
        return vals

    def _prepare_vals_shipments(self, order, picking, weight,customs):
        vals = { 'shipments':[] }
        vals['shipments'].append(self._prepare_vals_create_draft(order, picking, weight))
        if picking.packlink_pro_customs_required:
            vals['shipments'].append({'customs': customs })
        return vals

    def _prepare_vals_create_draft(self, order, picking, weight):
        vals = {
            'from':
                {
                    'name': "Susanna",
                    'surname': "Fort Mancha",
                    'company': self.env.company.name,
                    'phone': self.env.company.phone,
                    'email': self.env.company.email,
                    'street1': self.env.company.street,
                    'city': self.env.company.city,
                    'zip_code': self.env.company.zip,
                    'country': self.env.company.country_id.code,
                    'state': self.env.company.state_id.code,
                },
            'content': "Zynthian KIT v5.1",
            'contentvalue': order['amount_untaxed'],
            'service_id': order.packlink_pro_service_selected_id,
            'source': order.name,
            'packages': [
                {'height': picking.packlink_pro_height,
                 'length': picking.packlink_pro_length,
                 'width': picking.packlink_pro_width,
                 'weight': weight
                 }],
            'to':
                {
                    'name': picking.partner_id.name.split(" ", 1)[0] or picking.partner_id.name,
                    'surname': picking.partner_id.name.split(" ", 1)[1] or picking.partner_id.name,
                    'phone': picking.partner_id.phone,
                    'email': picking.partner_id.email,
                    'street1': picking.partner_id.street,
                    'city': picking.partner_id.city,
                    'zip_code': picking.partner_id.zip,
                    'state': picking.partner_id.state_id.code,
                    'country': picking.partner_id.country_id.code
                }
        }

        return vals

    def _prepare_customs_vals(self, value, weight, shipment_type, personal_id):
        # shipment_type: commercial_sale, gift, document, return
        vals = {
                'sender_type': 'private',
                'shipment_type': shipment_type,
                'sender_personalid': personal_id, #only fi shipment_type = commercial_sale
                'items':[{
                    'description_english': 'Zynthian KIT v5.1',
                    'quantity': 1,
                    'weight': (weight - 0.02),
                    'value': value,
                    'country_of_origin': 'ES',
                }],
        }
        return vals

    def packlink_pro_get_tracking_link(self, picking):
        packlink_pro_request = PacklinkProRequest(self)
        details = packlink_pro_request.get_shipment_details(picking.packlink_pro_reference)
        return details['tracking_url']

    def packlink_pro_get_label(self, pickings):
        for picking in pickings:
            response = PacklinkProRequest(self).get_label(picking.carrier_tracking_ref)
            if response:
                self.env["ir.attachment"].create(
                    {
                        "name":  "label-%s.%s" % (picking.group_id.name, 'pdf'),
                        "type": "binary",
                        "res_model": picking._name,
                        "res_id": picking.id,
                        "datas": base64.b64encode(response.content),
                    }
                )
        return response

    def packlink_pro_get_customs(self, pickings):
        response = []
        for picking in pickings:
            details = PacklinkProRequest(self).get_shipment_details(picking.carrier_tracking_ref)
            #_logger.info("CUSTOMS %s\n", details)
            response = PacklinkProRequest(self).get_customs(details['customs']['customs_invoice_id'])
            if response:
                self.env["ir.attachment"].create(
                    {
                        "name":  "customs-%s.%s" % (picking.group_id.name, 'pdf'),
                        "type": "binary",
                        "res_model": picking._name,
                        "res_id": picking.id,
                        "datas": base64.b64encode(response.content),
                    }
                )
        return response

    def packlink_pro_rate_shipment(self, order):
        price = 0.0
        packlink_pro_request = PacklinkProRequest(self)
        vals = self._prepare_packlink_pro_order(order)
        res = packlink_pro_request.get_services(vals)
        for r in res:
            try:
                if (self.dropoff == r['dropoff']  and
                     self.delivery_to_parcelshop == r['delivery_to_parcelshop'] and
                     (r['price']['base_price'] < price or price == 0.0)):
                    price = r['price']['base_price']
                    order.packlink_pro_service_selected = r['carrier_name']
                    order.packlink_pro_service_selected_id = r['id']
                    order.packlink_pro_customs_required = r['customs_required']
                    #_logger.info("%s - %s (%s) %s %i\n",r['id'],r['carrier_name'], r['price']['base_price'], order.packlink_pro_service_selected,order.packlink_pro_service_selected_id)
                    _logger.info("%s\n",r)
            except:
                pass
        if price == 0.0:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error: Doesn t find rate shipment for this destination, contact with sales@zynthian.org'),
                    'warning_message': False}
        else:
            return {
                "success": True,
                "price": price,
                "error_message": False,
                "warning_message": False,
            }

    def packlink_pro_send_shipping(self, pickings):
        customs = []
        res = []
        result = []
        packlink_pro_request = PacklinkProRequest(self)
        for p in pickings:
            if p.picking_type_code == "outgoing":
                # Es busca el SO enlloc de validar el que realment s'envia per facilitat incongruència amb el que ha pagat el client
                order = self.env['sale.order'].search([('name', '=', p.origin)])
                p.packlink_pro_customs_required = order.packlink_pro_customs_required
                p.packlink_pro_length, p.packlink_pro_height, p.packlink_pro_width, weight = self._prepare_order_package(order)
                p.packlink_pro_service_selected = order.packlink_pro_service_selected
                p.packlink_pro_service_selected_id = order.packlink_pro_service_selected_id
                _logger.info("Web Package (length x height x width) %f x %f x %f - Weight %f\n", p.packlink_pro_length, p.packlink_pro_height, p.packlink_pro_width,
                             weight)
                vals = self._prepare_vals_create_draft(order, p, weight)

                if self.draft:
                    result = packlink_pro_request.post_create_draft(vals)
                    p.packlink_pro_reference = result['reference']
                    details = packlink_pro_request.get_shipment_details(p.packlink_pro_reference)
                    price = details['price']['base_price']

                else:
                    if p.packlink_pro_customs_required:
                        customs = self._prepare_customs_vals(order['amount_untaxed'], weight, self.default_shipment_type, self.env.company.vat)
                    shipments = self._prepare_vals_shipments(order, p, weight, customs)
                    _logger.info("Shippments: %s\n", shipments)
                    result = packlink_pro_request.post_create_order(shipments)
                    p.packlink_pro_reference = result['shipments'][0]['shipment_reference']
                    price = result['shipments'][0]['total_price']


                if price is None:
                    price = 0.0

                res.append(
                    {
                        "exact_price": price,
                        "tracking_number": p.packlink_pro_reference,
                    }
                )

        return res