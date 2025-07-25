# Copyright 2021 Studio73 - Ethan Hildick <ethan@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)..
import logging

import requests

from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
PACKLINK_PRO_LABEL_TYPE = [("1", "PDF"), ("2", "ZPL")]
PACKLINK_PRO_SHIPMENT_TYPE = [
    ('commercial_sale', 'COMMERCIAL SALE'),
    ('gift', 'GIFT'),
    ('document', 'DOCUMENT'),
    ('return', 'RETURN'),
]
PACKLINK_PRO_SERVICE = [
    ("61", "PAQ10"),
    ("62", "PAQ14"),
    ("63", "PAQ24"),
    ("66", "BALEARES"),
    ("67", "CANARIAS EXPRES"),
    ("68", "CANARIAS AEREO"),
    ("69", "CANARIAS MARITIMO"),
    ("90", "INTERNACIONAL ESTANDAR"),
    ("91", "INTERNACIONAL EXPRES"),
    ("92", "PAQ EMPRESA 14"),
    ("93", "EPAQ24"),
    ("27", "CAMPAÑA CEX"),
    ("53", "53 ENTREGA + MANIPULACION LOINEX"),
    ("54", "54 ENTREGA + RECOGIDA LOINEX"),
    ("55", "55 ENTREGA + RECOGIDA + MANIPULA LOINEX"),
    ("73", "CHRONO PORTUGAL OPTICA"),
    ("76", "PAQUETERIA OPTICAS"),
    ("77", "OPTICA PREPAGADO"),
]


TEST_PATH = "https://apisandbox.packlink.com"
PROD_PATH = "https://api.packlink.com"


class PacklinkProRequest(object):
    def __init__(self, carrier):
        self.carrier_id = carrier
        path = PROD_PATH if self.carrier_id.prod_environment else TEST_PATH
        self.headers = {'Authorization': self.carrier_id.packlink_pro_api,
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'}
        self.urls = {
            "login": path + "/v1/users/api/keys",
            "services": path + "/pro/services",
            "available_services_details": path + "/v1/services/available/{identifier}/details",
            "create_order": path + "/v1/orders",
            "create_draft": path + "/v1/shipments",
            "label": path + "/v1/shipments/{id}/labels",
            "customs": path + "/v1/customs-invoice/{shipment_reference}/download",
            "shipments": path + "/v1/shipments",
            "shipment_detail": path + "/v1/shipments/{shipment_reference}",
            "track_shipment": path + "/v1/shipments/{id}/track",
        }

        r = requests.get(self.urls['login'], headers=self.headers, auth=None)
        _logger.info("STATUS %s\n",r.status_code)
        if r.status_code == '200':
            self.headers = {'Authorization': r.json()['token'],
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'}


    def _send_api_request(self, request_type, url, data=None, skip_auth=False):
        if data is None:
            data = {}
        result = {}
        _logger.info("URL: %s", url)
        try:
            if request_type == "GET":
                res = requests.get(url=url, auth=None, headers=self.headers, timeout=60)
            elif request_type == "POST":
                res = requests.post(url=url, auth=None, headers=self.headers, json=data, timeout=60)
            else:
                raise UserError(
                    _("Unsupported request type, please only use 'GET' or 'POST'")
                )
            result = res.json()
            packlink_pro_last_request = ("URL: {}\nData: {}").format(url, data)
            self.carrier_id.log_xml( packlink_pro_last_request, "packlink_pro_last_request")
            self.carrier_id.log_xml(result, "packlink_pro_last_response")

            res.raise_for_status()
        except requests.exceptions.Timeout as tmo:
            raise UserError(_("Timeout: the server did not reply within 60s")) from tmo
        except Exception as e:
            raise UserError(
                _("{error}\n{result}".format(error=e, result=result if result else ""))
            ) from e
        return_code, message = self._check_for_error(res)
        if return_code != 200 and return_code != 201:
            raise UserError(
                _("Packlink PRO Error: {return_code} {message}").format(
                    return_code=return_code, message=message
                )
            )
        return res

    def _check_for_error(self, result):
        message = "Webservice ERROR."
        return_code = result.status_code
        if return_code == 400:
            message = "Bad Request"
        elif return_code == 401:
            message = "UnAuthorized"
        elif return_code == 500:
            message = "Internal Error"
        else:
            message = "Ok"

        return return_code, message

    def get_services(self, vals):
        res = self._send_api_request(
            request_type="POST", url=self.urls["services"], data=vals
        )
        _logger.info("GET SERVICES: %s", res)
        return res.json()

    def get_track_shipment(self, vals):
        self.urls["track_shipment"].replace("{id}", vals["id"])
        res = self._send_api_request(
            request_type="GET", url=self.urls["track_shipment"], data=vals
        )
        _logger.info("GET SERVICES: %s", res)
        return res.json()

    def get_label(self, vals):
        result = []
        res = self._send_api_request(request_type="GET", url=self.urls["label"].format(id=vals))
        _logger.info("GET get_label: %s", res.json())
        if res.json():
            result = requests.get(url=res.json()[0])
        return result

    def get_customs(self, vals):
        result = []
        res = self._send_api_request(request_type="GET", url=self.urls["customs"].format(shipment_reference=vals))
        _logger.info("GET get_customs: %s", res)
        #if res.json():
        #    result = requests.get(url=res.json()['url'])
        return result

    def post_create_draft(self, vals):
        res = self._send_api_request(
            request_type="POST", url=self.urls["create_draft"], data=vals
        )
        _logger.info("POST post_create_draft: %s", res.json())
        return res.json()

    def post_create_order(self, vals):
        res = self._send_api_request(
            request_type="POST", url=self.urls["create_order"], data=vals
        )
        _logger.info("POST post_create_order: %s", res.json())
        return res.json()

    def get_shipment_details(self, vals):
        res = self._send_api_request(request_type="GET", url=self.urls["shipment_detail"].format(shipment_reference=vals))
        _logger.info("GET get_shipment_details: %s", res.json())
        return res.json()