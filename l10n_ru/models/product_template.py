from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_code = fields.Char(
        help="""The field is used as a product code
     in the document template 'UPD', 'Invoice', 'Act'.
     
     If this is not a product, but a service,
     then you need to specify the 'ОКВЕД' service code https://код-оквэд.рф"""
    )
