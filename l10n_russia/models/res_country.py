# -*- coding: utf-8 -*-

from odoo import fields, models


class Country(models.Model):
    _inherit = "res.country"

    number_code = fields.Char(string="Number code", size=3)
    l10n_ru_short_name = fields.Char(
        string="Short name",
        translate=True,
        help="In some cases is required to use shortened name. This is it.",
    )


class CountryState(models.Model):
    _inherit = "res.country.state"

    number_code = fields.Char(string="Number code", size=3)
