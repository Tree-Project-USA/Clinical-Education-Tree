# -*- coding: utf-8 -*-

{
    'name': 'Clinical Placement Decision Making',
    'category': 'Services/Project',
    'summary': '',
    'version': '16.0',
    'description': "",
    'license': 'LGPL-3',
    'depends': ['base', 'base_address_extended', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/cron_servises.xml',
        # 'data/cpdm_tree_data.xml',
        
        
        'views/archive_views.xml',
        'views/facility_contract_views.xml',
        'views/geographical_history_views.xml',
        'views/geographical_views.xml',
        'views/hardship_request_views.xml',
        'views/medical_facility_views.xml',
        'views/placement_offer_views.xml',
        # 'views/placement_request_views.xml',
        'views/res_partner_views.xml',
        'views/scce_views.xml',
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
