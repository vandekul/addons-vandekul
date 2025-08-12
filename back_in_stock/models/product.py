# Copyright 2023 Vandekul (<https://github.com/vandekul>)
# License OPL-1 (https://www.odoo.com/documentation/16.0/legal/licenses.html#odoo-apps).

from odoo import _, api, fields, models

class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product"]

    def action_view_notify_emails(self):
        action = self.env['ir.actions.act_window']._for_xml_id('back_in_stock.act_stock_notification')
        action['domain'] =  [('id', 'in', self.stock_notification_partner_ids.ids)]
        return action