# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re



class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    partner_d = fields.Many2one('res.partner', string='Clinical Site')
    scce_ids = fields.One2many('res.partner','partner_d', string='SCCE')
    facility_id = fields.Many2one('medical.facility', string='Clinical Site')
    is_ci = fields.Boolean(string='Is CI', default=False)
    entry_level_pt_degree_earned = fields.Char(string="Entry-Level PT Degree earned")
    highest_degree_earned = fields.Char(string="Highest degree earned")
    degree_area = fields.Char(string="Degree Area")
    years_experience_ci = fields.Char(string="Years experience as CI")
    years_experience_clinician = fields.Char(string="Years experience as clinician")
    areas_expertise = fields.Char(string="Areas of Expertise")
    clinical_certification = fields.Char(string="Clinical Certification")
    specify_area = fields.Char(string="Specify Area")
    apta_credentialed_ci = fields.Char(string="Specify Area")
    other_ci_credential = fields.Char(string="Other CI Credential")
    professional_organization_membership = fields.Char(string="Professional organization membership")
    
    @api.onchange('scce_ids')
    def _onchange_scce_id(self):
        for res in self:
            # print(res.scce_id.id)
            scce_facility_id = self.env["scce.facility"].sudo().search([('scce_id', 'in', res.scce_ids.ids)])
            print(scce_facility_id,'<<<<<<<<<<<<<<<<<<<<<<<<<<<')
            medical_facility_id = self.env["medical.facility"].sudo().search([('scce_ids', 'in', scce_facility_id.ids)])
            print(medical_facility_id)
            #    medical_id = self.env["medical.facility"].sudo().search([('id', '=', facility_id.id)])
            if medical_facility_id:
                for x in medical_facility_id:
                    x.write({
                        'ci_ids': res.ids
                    })
            