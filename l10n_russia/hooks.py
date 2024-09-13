from odoo import api, SUPERUSER_ID


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.model.data"].search(
        [("module", "=", "uom"), ("model", "=", "uom.uom")]
    ).write({"noupdate": False})
