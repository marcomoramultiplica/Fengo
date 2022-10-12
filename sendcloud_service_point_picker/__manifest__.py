# -*- coding: utf-8 -*-
{
    'name': 'SendCloud Service Point Picker',
    'version': '15.0',
    'category': 'Warehouse',
    'summary': 'SendCloud Service Point Picker provide to select service point to customers in checkout page.',

    'depends': ['sendcloud_delivery','website_sale_delivery'],

    'data': [
            'views/delivery_sendcloud_templates.xml'
    ],

    'images': ['static/description/sendcloud_service_point_picker.png'],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'support@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        - SendCloud Service Point Picker
        - Send Cloud Service Point Picker
        - eCommerce
        - eCommerce Sendcloud
        - eCommerce Send cloud
        - Sendcloud eCommerce
        - Send cloud eCommerce
        - eCommerce Integration
        - Integration eCommerce
        - Send Cloud
        - Manage your Send Cloud operation from Odoo
        - Integration Send Cloud
        - Connector Send Cloud
        - Send Cloud Connector
        - Odoo Send Cloud Connector
        - Send Cloud integration
        - Send Cloud odoo connector
        - Send Cloud odoo integration
        - Send Cloud shipping integration
        - Send Cloud integration with Odoo
        - odoo Send Cloud integration
        - odoo integration with Send Cloud
        - all in one shipping software for e-commerce
        - Manage your SendCloud operation from Odoo
        - Integration SendCloud
        - Connector SendCloud
        - SendCloud Connector
        - Odoo SendCloud Connector
        - SendCloud integration
        - SendCloud odoo connector
        - SendCloud odoo integration
        - SendCloud shipping integration
        - SendCloud integration with Odoo
        - odoo integration apps
        - odoo SendCloud integration
        - odoo integration with SendCloud
        - shipping integation
        - shipping provider integration
        - shipper integration
        - TeqStars
        - TeqStars Integration
        """,

    'assets': {
        'web.assets_frontend': [
            'sendcloud_service_point_picker/static/js/send_cloud_delivery.js',
        ],
    },

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': '49.00',
    'currency': 'EUR',
}
