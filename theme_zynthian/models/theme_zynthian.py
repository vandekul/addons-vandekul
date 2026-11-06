# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import base64
import logging

from odoo import models
from odoo.tools.misc import file_open

_logger = logging.getLogger(__name__)


class ThemeZynthian(models.AbstractModel):
    _inherit = "theme.utils"

    @property
    def _footer_templates(self):
        return ["theme_zynthian.template_footer_zynthian"] + super()._footer_templates

    def _zyn_toggle(self, xml_ids, active):
        """Enable/disable views, skipping the ones whose module is not installed."""
        for xml_id in xml_ids:
            if not self.env.ref(xml_id, raise_if_not_found=False):
                _logger.info("theme_zynthian: view %s not found, skipped", xml_id)
                continue
            if active:
                self.enable_view(xml_id)
            else:
                self.disable_view(xml_id)

    def _theme_zynthian_post_copy(self, mod):
        # ---------------------------------------------------------------
        # Header: logo on the left, menu aligned to the right (like
        # shop.zynthian.org), black bar, always visible.
        # ---------------------------------------------------------------
        self.enable_view("website.template_header_default")
        self._zyn_toggle([
            "website.template_header_default_align_right",
            "website.no_autohide_menu",
        ], True)
        self._zyn_toggle([
            "website.template_header_default_align_center",
            "website.header_search_box",
            "website.header_text_element",
            "website.header_social_links",
            "website.header_call_to_action",
            "portal.user_sign_in",
        ], False)

        # ---------------------------------------------------------------
        # Footer: Grav "hola" footer (logo + social links + legal links)
        # ---------------------------------------------------------------
        self.enable_view("theme_zynthian.template_footer_zynthian")
        self._zyn_toggle(["website.option_footer_scrolltop"], True)

        # ---------------------------------------------------------------
        # Shop page (/shop): like shop.zynthian.org/shop/category/all-10
        # categories as buttons on top, no sidebar / search / sort /
        # filters, "add to cart" button on every product card.
        # ---------------------------------------------------------------
        self._zyn_toggle([
            "website_sale.products_categories_top",
            "website_sale.products_add_to_cart",
        ], True)
        self._zyn_toggle([
            "website_sale.products_categories",
            "website_sale.option_collapse_products_categories",
            "website_sale.sort",
            "website_sale.add_grid_or_list_option",
            "website_sale.products_attributes",
            "website_sale.products_attributes_top",
            "website_sale.filter_products_price",
            "website_sale.filter_products_tags",
            "website_sale.products_list_view",
            "website_sale.products_description",
        ], False)

        website = self.env["website"].get_current_website()
        if website:
            # 4 products per row, as in shop.zynthian.org
            website.shop_ppr = 4
            # Use the white Zynthian logo, unless a custom logo was already
            # uploaded (i.e. only replace Odoo's default website logo).
            if not website.logo or website.logo == website._default_logo():
                with file_open("theme_zynthian/static/src/img/logo.png", "rb") as f:
                    website.logo = base64.b64encode(f.read())
