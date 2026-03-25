# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    archive_ids = fields.One2many(comodel_name='archive', inverse_name='student_id', string='Placement History')
    aval_archive_ids = fields.Many2many(comodel_name='archive', string='Archive', compute='_compute_aval_archive_ids')
    is_take_ip = fields.Boolean(compute='_compute_is_take_ip', string='Is Take IP')   
    preferred_geographical_ids = fields.One2many(comodel_name='geographical.preferred', inverse_name='student_id', string='Preferred Addresses')
    preferred_setting_ids = fields.Many2many(comodel_name='preferred.setting', string='Preferred Setting')
    experience_schedual_ids = fields.Many2many(comodel_name='clinical.experience.schedual', compute='_compute_experience_schedual_ids', string='Student Experience Schedule')
    
    @api.depends('archive_ids')
    def _compute_aval_archive_ids(self):
        for rec in self:
            rec.aval_archive_ids = rec.archive_ids.filtered(lambda x: x.placement_status != 'not_placed')
            
    @api.depends('archive_ids')
    def _compute_is_take_ip(self):
        for rec in self:
            rec.is_take_ip = any(x.setting == 'ip' and x.placement_status != 'not_placed' for x in rec.archive_ids)

    # Note: Complex logic for experience_schedual_ids might need refactoring 
    # if it depends on graduation term calculations.
    def _compute_experience_schedual_ids(self):
        # Placeholder for matching logic - will be fully refactored as needed
        for rec in self:
            rec.experience_schedual_ids = False

    def get_accepted_distance_facility(self, facility_ids, facility_distance_mel=50):
        # Implementation from original res_partner.py
        facility_distance_mel = float(facility_distance_mel) or self.env.company.clinical_distance_mel or 50
        accepted_facility_ids = set()
        geographical_ids = self.preferred_geographical_ids.mapped('geographical_id')
        for geographical_id in geographical_ids:
            # Note: geographical_id.get_distance_with_multi_zip_codes must exist in cdm_base mapping
            distances = geographical_id.get_distance_with_multi_zip_codes([f.geographical_id for f in facility_ids])[0]
            accepted_facility_ids.update([f.id for f, distance in zip(facility_ids, distances) if distance <= facility_distance_mel])
        return list(accepted_facility_ids)

    def get_nearest_facility(self, department_ids):
        self.ensure_one()
        nearest_dept = False
        nearest_geo = False
        min_dist = float('inf')
        
        student_geos = self.preferred_geographical_ids.mapped('geographical_id')
        for s_geo in student_geos:
            for dept in department_ids:
                dist, _ = s_geo.get_distance_with_zip_code(dept.geographical_id)
                if dist < min_dist:
                    min_dist = dist
                    nearest_dept = dept
                    nearest_geo = s_geo
        return nearest_dept, nearest_geo

    def get_student_last_experience(self):
        self.ensure_one()
        # Returns the last clinical experience of the student from their schedule
        last_schedual = self.env['clinical.experience.schedual'].search([
            ('student_id', '=', self.id)
        ], order='sequence desc', limit=1)
        return last_schedual.experience_id
