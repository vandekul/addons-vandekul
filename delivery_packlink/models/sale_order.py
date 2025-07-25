from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    packlink_pro_service_selected = fields.Char(string='Carrier Name', help='Carrier Name Selected from Packlink PRO')
    packlink_pro_service_selected_id = fields.Integer(string='Carrier Name ID', help='Identifier from carrier selected Packlink PRO')
    packlink_pro_customs_required = fields.Boolean("Customs required", default=False)

    is_packlink_pro_delivery_type = fields.Boolean(
        compute="_compute_is_packlink_pro_delivery_type", store=True
    )

    @api.depends("carrier_id.delivery_type")
    def _compute_is_packlink_pro_delivery_type(self):
        for order in self:
            is_packlink_pro = order.carrier_id.delivery_type == "packlink_pro"
            order.is_packlink_pro_delivery_type = is_packlink_pro
