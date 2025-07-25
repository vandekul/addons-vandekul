# Copyright 2021 Studio73 - Ethan Hildick <ethan@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, models, fields
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    packlink_pro_reference = fields.Char(string='Packlink Reference', help='Packlink PRO Reference Package')
    packlink_pro_service_selected = fields.Char(string='Carrier Name', help='Carrier Name Selected from Packlink PRO')
    packlink_pro_service_selected_id = fields.Integer(string='Carrier Name ID', help='Identifier from carrier selected Packlink PRO')
    packlink_pro_length = fields.Float("Length")
    packlink_pro_height = fields.Float("Height")
    packlink_pro_width = fields.Float("Width")
    packlink_pro_customs_required = fields.Boolean("Customs required")



    def packlink_pro_get_label(self):
        self.ensure_one()
        if self.delivery_type != "packlink_pro":
            return
        return self.carrier_id.packlink_pro_get_label(self)


    def packlink_pro_get_customs(self):
        self.ensure_one()
        if self.delivery_type != "packlink_pro":
            return
        return self.carrier_id.packlink_pro_get_customs(self)