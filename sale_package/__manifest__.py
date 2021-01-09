# -*- coding: utf-8 -*-
{
    'name': "Sale Packages",

    'summary': """Manage sale packages""",
               
    'description': """Packages in Sale Module""",

    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Inventory/Inventory',
    'sequence': '10',
    'version': '14.0.2.1.2',
    'depends': ['base', 'stock', 'sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',


    ],
    'demo': [

    ],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
