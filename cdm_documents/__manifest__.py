# -*- coding: utf-8 -*-
{
    'name': 'CDM Clinical Documents',
    'category': 'Services/Project',
    'summary': 'Manage medical and site-required student documents',
    'version': '16.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['cdm_base', 'odx_m2m_attachment_preview'],
    'data': [
        'security/cdm_documents_security.xml',
        'security/ir.model.access.csv',
        'views/attachment_type_views.xml',
        'views/scce_attachment_type_views.xml',
        'views/res_partner_document_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
