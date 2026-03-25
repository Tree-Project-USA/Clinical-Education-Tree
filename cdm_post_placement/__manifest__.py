# -*- coding: utf-8 -*-
{
    'name': 'CDM Post-Placement Management',
    'category': 'Services/Project',
    'summary': 'Manage evaluations and post-placement tracking',
    'version': '16.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['cdm_base', 'survey', 'cdm_matching'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_post_placement_views.xml',
        'views/survey_survey_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
