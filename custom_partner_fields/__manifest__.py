# -*- coding: utf-8 -*-
{
    'name': "Custom res.partner fields",

    'summary': """Custom res.partner fields""",

    'description': """Custom res.partner fields""",

    'installable': True,
    'auto_install': False,
    'application': True,

    'author': "Deuse",
    'website': "https://deuse.be",

    'version': '14.0.0.0.1',

    'depends': ['base', 'school_management'],

    'data': [
        'views/res_partner_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'images': [
        'static/description/icon.png',
    ],
}