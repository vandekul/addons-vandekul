# -*- coding: utf-8 -*-

from odoo import fields, models


class Bank(models.Model):
    _inherit = "res.bank"

    corr_account = fields.Char(string="Corresponding account", index=True)
