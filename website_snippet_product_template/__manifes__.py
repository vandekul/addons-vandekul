# ******************************************************************************
# WEBSITE SNIPPET PRODUCTS TEMPLATE
#
# Copyright (C) 2024 Susanna Fort <susannafm@gmail.com>
#
# ******************************************************************************
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the LICENSE.txt file.
#
# ******************************************************************************
{
    'name': 'Website Snippet Products Template',
    'summary': 'This module is Snippet Products Template Carrousel',
    'author': 'Vande',
    'website': 'https://github.com/vandekul',
    'category': 'Theme/eCommerce',
    'version': '16.0',
    'license': 'GPL-3',
    'application': True,
    'depends': ['website', 'website_sale'],
    'data': ['data/data.xml',
             'views/snippets/s_dynamic_snippet.xml',
             'views/snippets/s_dynamic_snippet_products_filters.xml',
             ],
    'description': 'Snippet Products Template Carrousel',
    'images': ['static/description/favicon-black.png'],

    'installable': True,
    'auto_install': False,
}
