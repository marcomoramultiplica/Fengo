# -*- coding: utf-8 -*-
{
    'name': 'Sitemap URL Remover',
    'description': 'This remove the unwanted urls from the sutemap url for website.',
    'summary': 'Remove URLs from the sitemap for better search engine indexing',
    'category': 'Website',
    'version': '15.0.0.1',
    'author': "Magnetposts.com",
    'company': 'Magnetposts.com',
    'maintainer': 'Magnetposts',
    'website': "https://www.magnetposts.com",
    'currency': 'USD',
    'category': 'Website',
    'depends': ['website'],
    'data': [
        'security/ir.model.access.csv',
        'views/seo_seo_view.xml',
    ],
    'images': [
        'static/description/cover.gif',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
