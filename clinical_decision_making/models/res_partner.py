# -*- coding: utf-8 -*-
import requests
import json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class NamaModel(models.Model):
    _inherit = 'res.partner'
    
    is_student = fields.Boolean(string='Is Student', default=False)
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    cohort_label = fields.Char(string='Cohort Label')# TODO: Remoove this line
    hardship_ids = fields.One2many('hardship.request', 'student_id', string='Hardship')
    home_address = fields.Char(string='Home Address')
    archive_ids = fields.One2many(comodel_name='archive', inverse_name='student_id', string='Archive')
    geographical_history_ids = fields.One2many(comodel_name='geographical.history', inverse_name='student_id', string='geographical')
    can_apply_hardship = fields.Boolean(string='Apply Hardship', default=False)
    is_reach_maximum_zip_code = fields.Boolean(string='Reach Maximum Zip Code', default=False)
    deny_show_student = fields.Boolean()
    is_complete_ice = fields.Boolean(string='Is Complate Ice')
    is_complete_tce1 = fields.Boolean(string='Is Complate Tec1')
    is_complete_tce2 = fields.Boolean(string='Is Complate Tec2')
    geographical_ids = fields.Many2many(comodel_name='geographical', string='Geographical')
    program_type = fields.Selection([
        ('3', 'DET - Residential (3Year)'),
        ('4', 'DET - Flexible (4Year)'),
    ], string='Program Type', default='3', required=True)
    start_year = fields.Date(string='Start Year')
    start_term_type = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Start Term Type', required=True)
    start_term = fields.Char(string='Start Term', compute='_compute_term_fields', store=True)
    graduation_term = fields.Char(string='Graduation Term', compute='_compute_term_fields', store=True)
    is_with_hardship = fields.Boolean(string='is_with_hardship', compute='_compute_is_with_hardship')
    
    @api.depends('hardship_ids')
    def _compute_is_with_hardship(self):
        for rec in self:
            rec.is_with_hardship = True if self.env['hardship.request'].search([('student_id', '=', rec.id), ('confirm', '=', 'confirm')]) else False
            
    @api.depends('start_year', 'start_term_type', 'program_type')
    def _compute_term_fields(self):
        for rec in self:
            if rec.program_type == '3':...
                
            rec.start_term = 'Test Case'
            rec.graduation_term = 'Test Case'
    
    @api.onchange('geographical_ids')
    def _onchange_geographical_ids(self):
        if not self.env.context.get('has_hardship') or not self.is_with_hardship:
            for rec in self.geographical_ids:
                if rec.id in self.geographical_ids.filtered(lambda x : x.id != rec.id).mapped('id'):
                    raise ValidationError(_('Zip code must be unique. '))
            self.check_zip_code_distance(self.geographical_ids)

    @api.onchange('first_name', 'last_name')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.first_name if rec.first_name else '' + ', ' + rec.last_name if rec.last_name else ''
    
    def check_zip_code_distance(self, geographical_ids):
        max_distance_mel = self.env['ir.config_parameter'].sudo(
        ).get_param('max_distance_mel')
        
        for geographical_id in geographical_ids:
            zipcoe_ids, dis_and_geo = geographical_id.get_distance_with_multi_zip_codes(geographical_ids - geographical_id)
            for zip_code, distance in dis_and_geo.items():
                if distance < float(max_distance_mel):
                    raise ValidationError(_('The Distance Between zip codes (%s) and (%s) is (%s) and  too small that the distance required to (%s) miles'% (geographical_id.zip_code , zip_code.zip_code, distance, max_distance_mel)))
    
    def check_validation_zip_code_state(self, geographical_ids):
        max_zipcodes_state = self.env['ir.config_parameter'].sudo().get_param('max_zipcodes_state') or 3
        max_zipcodes_state = int(max_zipcodes_state)
        max_distance_mel = self.env['ir.config_parameter'].sudo(
        ).get_param('max_distance_mel')
        
        for geographical_id in geographical_ids:
            zipcoe_ids, dis_and_geo = geographical_id.get_distance_with_multi_zip_codes(geographical_ids - geographical_id)
            for zip_code, distance in dis_and_geo.items():
                if distance < float(max_distance_mel):
                    raise ValidationError(_('The Distance Between zip codes (%s) and (%s) is (%s) and  too small that the distance required to (%s) miles'% (geographical_id.zip_code , zip_code.zip_code, distance, max_distance_mel)))
    
    @api.constrains('geographical_ids')
    def _check_geographical_ids(self):
        self.ensure_one()
        if not self.env.context.get('has_hardship') or not self.is_with_hardship:
            normal_number_zipcodes = self.env['ir.config_parameter'].sudo().get_param('normal_number_zipcodes') or 5
            normal_number_zipcodes = int(normal_number_zipcodes)
           
            if len(self.geographical_ids) < normal_number_zipcodes or len(self.geographical_ids) > normal_number_zipcodes:
                    raise ValidationError(_('Lenth of zip codes shuld be %s' % normal_number_zipcodes))
                
            for rec in self.geographical_ids:
                if rec.id in self.geographical_ids.filtered(lambda x : x.id != rec.id).mapped('id'):
                    raise ValidationError(_('Zip code must be unique. '))
            self.check_zip_code_distance(self.geographical_ids)
    