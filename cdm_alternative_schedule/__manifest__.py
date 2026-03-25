# -*- coding: utf-8 -*-
{
    'name': 'CDM Alternative Schedule',
    'category': 'Services/Project',
    'summary': 'Manage deviations from standard student placement schedules',
    'version': '16.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['cdm_base'],
    'data': [
        'security/cdm_alt_schedule_security.xml',
        'security/ir.model.access.csv',
        'views/alternative_schedule_views.xml',
        'views/res_partner_alt_schedule_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
