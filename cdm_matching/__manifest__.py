# -*- coding: utf-8 -*-
{
    'name': 'CDM Placement & Matching',
    'category': 'Services/Project',
    'summary': 'Clinical Placement logic and Student-to-Site Matching',
    'version': '16.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['cdm_base', 'cdm_hardship'],
    'data': [
        'security/cdm_matching_security.xml',
        'security/ir.model.access.csv',
        'data/tree_data.xml',
        'views/placement_request_views.xml',
        'views/placement_offer_views.xml',
        'views/archive_views.xml',
        'views/res_partner_matching_views.xml',
        'views/matching_extensions.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
