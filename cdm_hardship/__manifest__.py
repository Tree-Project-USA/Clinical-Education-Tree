# -*- coding: utf-8 -*-
{
    'name': 'CDM Hardship Management',
    'category': 'Services/Project',
    'summary': 'Manage student hardship requests',
    'version': '16.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['cdm_base'],
    'data': [
        'security/cdm_hardship_security.xml',
        'security/ir.model.access.csv',
        'data/mail_data.xml',
        'views/hardship_request_views.xml',
        'views/res_partner_hardship_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
