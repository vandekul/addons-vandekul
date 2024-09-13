# -*- coding: utf-8 -*-

from odoo import fields, models


class Currency(models.Model):
    _inherit = "res.currency"

    number_code = fields.Char(string="Number code", size=3)
