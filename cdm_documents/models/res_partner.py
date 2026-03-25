# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def get_default_required_document(self):
        attachment = []
        for type_id in self.env['attachment.type'].search([]):
             attachment += [(0, 0, {
                'company_id': self.env.user.company_id.id,
                'attachment_type': type_id.id,
             })]
        return attachment
    
    def get_default_scce_document(self):
        attachment = []
        for type_id in self.env['scce.attachment.type'].search([]):
             attachment += [(0, 0, {
                'company_id': self.env.user.company_id.id,
                'scce_attachment_type': type_id.id,
             })]
        return attachment
    
    medical_attachment_ids = fields.One2many(comodel_name='attachments', inverse_name='student_id', string='Required Document', default=get_default_required_document)
    scce_medical_attachment_ids = fields.One2many(comodel_name='scce.attachments', inverse_name='student_id', string='SCCE Required Document', default=get_default_scce_document)
