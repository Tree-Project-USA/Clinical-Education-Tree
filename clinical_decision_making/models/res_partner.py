# -*- coding: utf-8 -*-
import requests
import json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(1999, 2500)]


class NamaModel(models.Model):
    _inherit = 'res.partner'
    
    is_student = fields.Boolean(string='Is Student', default=False)
    first_name = fields.Char(string='First Name', )
    last_name = fields.Char(string='Last Name', )
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
    program_id = fields.Many2one(comodel_name='program', string='Program', )
    start_term_type = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Start Term Type', )
    start_year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year', )
    start_term = fields.Char(string='Start Term', compute='_compute_term_fields', store=True)
    graduation_term = fields.Char(string='Graduation Term', compute='_compute_term_fields', store=True)
    is_with_hardship = fields.Boolean(string='is_with_hardship', compute='_compute_is_with_hardship')
    
    @api.depends('hardship_ids')
    def _compute_is_with_hardship(self):
        for rec in self:
            rec.is_with_hardship = True if self.env['hardship.request'].search([('student_id', '=', rec.id), ('state', '=', 'confirm')]) else False
            
    @api.depends('start_year', 'start_term_type', 'program_id')
    def _compute_term_fields(self):
        for rec in self:
            if rec.start_year and rec.start_term_type  and rec.program_id:
                rec.start_term = self.convert_term_year(rec.start_term_type, rec.start_year)
                graduation_t, graduation_y = rec.calculate_end_term(rec.start_term_type, rec.start_year, rec.program_id.num_terms)
                rec.graduation_term = self.convert_term_year(graduation_t, graduation_y)
            else:
                rec.start_term = ''
                rec.graduation_term = ''
    
    # @api.onchange('geographical_ids')
    # def _onchange_geographical_ids(self):
    #     self.ensure_one()
    #     if not self.env.context.get('has_hardship', False) or not self.is_with_hardship:
    #         print(self.geographical_ids)
    #         for rec in self.geographical_ids:
    #             if rec.id in self.geographical_ids.filtered(lambda x : x.id != rec.id).mapped('id'):
    #                 raise ValidationError(_('Zip code must be unique. '))
    #         self.check_zip_code_distance(self.geographical_ids)
    #         self.check_validation_zip_code_state(self.geographical_ids)

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

        for geographical_id in geographical_ids:
            zipcoe_ids = geographical_id.get_zip_codes_state(geographical_ids - geographical_id)
            if len(zipcoe_ids) < max_zipcodes_state:
                    raise ValidationError(_('You can only add maximum (%s) zip code in same state' % max_zipcodes_state))
    
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
            self.check_validation_zip_code_state(self.geographical_ids)
            
    
    def calculate_end_term(self, start_term, start_year, num_terms):
        terms = ["spring", "summer", "fall"]
        start_index = terms.index(start_term)
        current_index = start_index
        current_year = int(start_year)

        # Calculate the end term
        for _ in range(num_terms - 1):
            current_index += 1
            if current_index == len(terms):
                current_index = 0
                current_year += 1

        return terms[current_index], current_year
    
    def convert_term_year(self, term, year):
        term_abbr = ""
        if term.lower() == "fall":
            term_abbr = "FA"
        elif term.lower() == "spring":
            term_abbr = "SP"
        elif term.lower() == "summer":
            term_abbr = "SU"

        year_abbr = str(year)[-2:]

        term_year = term_abbr + year_abbr

        return term_year

