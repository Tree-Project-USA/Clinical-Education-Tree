# -*- coding: utf-8 -*-

from datetime import date

from odoo import models, fields, api
from odoo.exceptions import ValidationError


SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]

class Program(models.Model):
    _name = 'program'
    _description = 'Student Program'
    _rec_name = 'name'
    
    name = fields.Char(string='Program Name')
    num_terms = fields.Integer(string='Number of terms', default=1)
    active = fields.Boolean(string='Status')
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)
    program_experience_term_ids = fields.One2many(comodel_name='program.experience.term', inverse_name='program_id', string='Program Clinical Experience Terms', store=True)
    
    def action_open_program_experience_term(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.program_action')
        action['context'] = {'create': False, 'delete': False, 'default_program_id': self.id}
        action.update({
            'view_mode': 'form',
            'view_id': self.env.ref('clinical_decision_making.program_view_form').id,
            'views': [(self.env.ref('clinical_decision_making.program_view_form').id, 'form')],
            'res_id': self.id,
            'target': 'new'
        })
        return action
    
    def create_update_program_experience_term(self):
        self.ensure_one()
        records = []
        experience_ids = self.env['clinical.experience'].search([('company_id', '=', self.company_id.id)])
        for experience_id in experience_ids:
            if experience_id.id not in self.program_experience_term_ids.mapped('experience_id').ids:
                records += [(0,0, {
                    'program_id': self.id,
                    'company_id': self.company_id.id,
                    'experience_id': experience_id.id,
                    'term': 0
                })]
        self.write(
            {'program_experience_term_ids': records}
        )
        
    @api.model
    def create(self, values):
        # Add code here
        res = super(Program, self).create(values)
        res.create_update_program_experience_term()
        return res
    
    
    @api.constrains('num_terms', 'program_experience_term_ids', 'program_experience_term_ids.term')
    def _check_num_terms(self):
        for rec in self:
            for record in rec.program_experience_term_ids:
                if rec.num_terms < record.term:
                    print((record.experience_id.name, record.term, rec.name, rec.num_terms))
                    raise ValidationError("The Clinical Experience (%s) with term number (%s) is greater than Program Duration (%s) (%s) terms. " % (record.experience_id.name, record.term, rec.name, rec.num_terms))
            

class ProgramExperienceTerm(models.Model):
    _name = 'program.experience.term'
    _description = 'Program Clinical Experience Term'
    _rec_name = 'program_id'
    _order = "sequence"
    
    program_id = fields.Many2one(comodel_name='program', string='Program')
    company_id = fields.Many2one('res.company', related='program_id.company_id', store=True)
    experience_id = fields.Many2one(comodel_name='clinical.experience', string='Clinical Experience')
    sequence = fields.Char(related='experience_id.sequence', store=True)
    term = fields.Integer(string='term Number', default=1)
    date_ids = fields.One2many(comodel_name='program.experience.dates', inverse_name='program_term_id', string='Program Dates')
    
    def action_open_program_experience_dates(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.action_program_experience_term')
        action['context'] = {'delete': False, 'default_program_term_id': self.id}
        action.update({
            'view_mode': 'form',
            'view_id': self.env.ref('clinical_decision_making.program_experience_term_view_form').id,
            'views': [(self.env.ref('clinical_decision_making.program_experience_term_view_form').id, 'form')],
            'res_id': self.id,
            'target': 'new'
        })
        return action

class ProgramExperienceTermDates(models.Model):
    _name = 'program.experience.dates'
    _description = 'Program Clinical Experience Dates'
    _rec_name = 'program_term_id'
    _order = "year"
    
    program_term_id = fields.Many2one(comodel_name='program.experience.term', string='Program Experience Term')
    company_id = fields.Many2one('res.company', related='program_term_id.company_id', store=True)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year', required=True)
    
    fa_start_date = fields.Date(string='Fall start Date')
    fa_end_date = fields.Date(string='Fall End Date')
    
    sp_start_date = fields.Date(string='Spring start Date')
    sp_end_date = fields.Date(string='Spring End Date')
    
    su_start_date = fields.Date(string='Summer start Date')
    su_end_date = fields.Date(string='Summer End Date')
    
    _sql_constraints = [
        ("year_check", "check(program_term_id,year)", "Year is already exsist"),
    ]
    
    @api.onchange('year',
                  'fa_start_date',
                  'fa_end_date',
                  'sp_start_date',
                  'sp_end_date',
                  'su_start_date',
                  'su_end_date'

                  )
    def _onchange_field(self):
        for rec in self:
            if rec.year:
                year = int(rec.year)
                
                rec.fa_start_date = date(year, rec.fa_start_date.month, rec.fa_start_date.day) if rec.fa_start_date else False
                rec.fa_end_date = date(year, rec.fa_end_date.month, rec.fa_end_date.day) if rec.fa_end_date else False
                
                rec.sp_start_date = date(year, rec.sp_start_date.month, rec.sp_start_date.day) if rec.sp_start_date else False
                rec.sp_end_date = date(year, rec.sp_end_date.month, rec.sp_end_date.day) if rec.sp_end_date else False
                
                rec.su_start_date = date(year, rec.su_start_date.month, rec.su_start_date.day) if rec.su_start_date else False
                rec.su_end_date = date(year, rec.su_end_date.month, rec.su_end_date.day) if rec.su_end_date else False

    