# -*- coding: utf-8 -*-

{
    'name': 'Clinical Placement Decision Making',
    'category': 'Services/Project',
    'summary': '',
    'version': '16.0',
    'description': "",
    'license': 'LGPL-3',
    'depends': ['base', 'base_address_extended'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_servises.xml',
        'views/setting_views.xml',
        'views/cohort_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_views.xml',
        'views/menu.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'clinical_decision_making/static/src/scss/main.scss',

        ],

        
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
