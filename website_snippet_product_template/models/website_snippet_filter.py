# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.tools.image import image_data_uri
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)
class WebsiteSnippetFilter(models.Model):
    _inherit = 'website.snippet.filter'

    def _get_products_attr_value_filter(self, website, limit, domain, context):
        search_domain = context.get('search_domain')
#        _logger.info("ENTREM!!!!!!!!!!!!!!!!!!!!!!\n DOMAIN: %s\n CONTEXT:%s\n VALUES1:%s\n DOMAIN PARAM:%s\n WEBSITE:%s\n SELF:%s\n",
#                     context.get('search_domain'),  context, context.get('dynamic_filter'), domain, self.env['website'].get_current_website().website_domain(), self)

        result = self.filter_attribute(search_domain)
        _logger.info(f"Product Attr: {result}\n, search_domain: {search_domain}\n")

        domain = search_domain or []
        if result['attrs']:
            domain = expression.AND([
                domain,
                [("product_template_attribute_value_ids.attribute_id.name", "in", result['attrs'])],
            ])

        if result['values']:
            domain = expression.AND([
                domain,
                [("product_template_attribute_value_ids.product_attribute_value_id.name","in", result['values'])],
            ])

        _logger.info(f"Domain: {domain}\n")
        products = self.env['product.product'].search(domain)
        _logger.info(f"Products: {products}\n")
        return products

    def filter_attribute(self, data):
        res = {
            "attrs": [],
            "values": []
        }
        for i, item in enumerate(data):
            if item[0] == "attribute_value_name":
                for variant in item[2]:
                    parts = variant.split(":", 2)
                    if len(parts) > 1:
                        res['attrs'].append(parts[0].strip())
                        res['values'].append(parts[1].strip())
                res['attrs'] = list(set(res['attrs']))
                del data[i]
                break
        return res



