# -*- coding: utf-8 -*-
{
    "name": "Russian Localization",
    "summary": """
        Adds russian respecific requisites for juridical and physical persons""",
    "description": """Adds next requisites:\n
        - Passport series and number,\n
        - Passport issue date,\n
        - Department issued the passport,\n
        - IEC - Industrial Enterprises Classifier,\n
        - PSRN - Primary State Registration Number,\n
        - OKPO - All-Russian Classifier of Enterprises and Organizations,\n
        - Bank corresponding account.
    """,
    "author": "RYDLAB",
    "website": "https://rydlab.ru",
    "category": "Accounting/Localizations/Account Charts",
    "version": "16.0.1.0.1",
    "depends": ["base", "account", "uom", "product"],
    "pre_init_hook": "pre_init_hook",
    "data": [
        "data/account_chart_template.xml",
        "data/account_chart.xml",
        "data/account.account.template.csv",
        "data/res.partner.title.csv",
        "data/account_tax_group_data.xml",
        "data/account_tax_template.xml",
        "data/account_chart_template_data.xml",
        "data/res_country_data.xml",
        "data/res_country_state_data.xml",
        "data/res_currency_data.xml",
        "data/uom_data.xml",
        "views/partner.xml",
        "views/bank.xml",
        "views/res_country_views.xml",
        "views/res_currency_views.xml",
        "views/uom_uom_views.xml",
    ],
    "license": "LGPL-3",
    "images": ["static/description/banner.png"],
}
