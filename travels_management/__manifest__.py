# -*- coding: utf-8 -*-
{
    'name': "Travels Management",

    'summary': """Travels Management Software""",

    'description': """Application For Travels Management""",

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '14.0.2.1.2',

    'depends': ['base', 'mail', 'uom'],

    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/service_type.xml',
        'data/booking_expiry_cron.xml',
        'views/travels.xml',
    ],
    'demo': [

    ],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
