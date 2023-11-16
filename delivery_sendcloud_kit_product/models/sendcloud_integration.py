# Copyright 2023 Vandekul (<https://github.com/vandekul>)
# License OPL-1 (https://www.odoo.com/documentation/16.0/legal/licenses.html#odoo-apps).

from odoo import api, models, fields, _

class SendcloudIntegrationKitProduct(models.Model):
    _name = 'sendcloud.integration'
    _inherit = ['sendcloud.integration']
    _description = 'Sendcloud Integration KIT product'

    kit_product = fields.Boolean("Kit Product",
                                 default=False,
                                 help="If it's set KIT products will be sent to sendcloud like one product and not like it's components")
