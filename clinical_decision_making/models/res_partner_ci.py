# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    partner_d = fields.Many2one('res.partner', string='Clinical Site')
    scce_ids = fields.Many2many('res.partner', 'scce_id_rel', 'partner_id_rel',  string="Scce" ,domain=[('is_scce', '=', True)]) 
    # scce_ids = fields.Many2many('scce.facility', string='SCCE' ,domain=[('is_primary_scce', '=', True), ('scce_id','!=',False)]) 
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
    ci_details_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('completed', 'Completed'),
    ], string='CI Details Status',)
    
    
    @api.onchange('scce_ids')
    def _onchange_scce_id(self):
        for res in self:
            medical_facility_id = self.env["scce.facility"].sudo().search([('scce_id', 'in', res.scce_ids.ids)])
            if medical_facility_id:
                for x in medical_facility_id:
                    x.facility_id.write({
                        'ci_ids': [Command.link(res.ids[0])]
                    })
            medical_facility = self.env["scce.facility"].sudo().search([('scce_id', 'not in', res.scce_ids.ids)])
            if medical_facility:
                for x in medical_facility:
                    x.facility_id.write({
                        'ci_ids': [Command.unlink(res.ids[0])] if res.ids else []
                    })
           
                
    