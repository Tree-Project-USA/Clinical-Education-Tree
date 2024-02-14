# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re



class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    scce_id = fields.Many2one('res.partner', string='SCCE', domain=[('is_scce', '=', True)], required=True)
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