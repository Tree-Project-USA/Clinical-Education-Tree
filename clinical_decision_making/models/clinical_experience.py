# -*- coding: utf-8 -*-
import logging
from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]


class C33linicalExperience(models.Model):
    _name = 'program.experience.dates'
    
class ClinicalExperience(models.Model):
    _name = 'clinical.experience'
    _description = _('Clinical Experience')
    _order = "sequence"

    active = fields.Boolean(string='Status')
    name = fields.Char(string='Clinical Experience Name')
    sequence = fields.Char(
        'Sequence', default=lambda self: self.env['ir.sequence'].next_by_code('clinical.experience'), company_dependent=True)
    ptse_2_survey = fields.Many2one('survey.survey', string="PTSE 2 Survey", domain=[('ptse_type', '=', 'ptse_2')])
    ptse_1_survey = fields.Many2one('survey.survey', string="PTSE 1 Survey", domain=[('ptse_type', '=', 'ptse_1')])
    company_id = fields.Many2one('res.company', string='Program', default=lambda self: self.env.user.company_id)
    date_ids = fields.One2many(comodel_name='clinical.experience.dates', inverse_name='experience_id', string='Program Dates')
    
    def action_open_experience_dates(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.action_clinical_experience')

        action['context'] = {'delete': False, 'default_experience_id': self.id}
        action.update({
            'name': '%s Clinical Experience Dates' % self.name,
            'view_mode': 'form',
            'view_id': self.env.ref('clinical_decision_making.clinical_experience_dates_view_form').id,
            'views': [(self.env.ref('clinical_decision_making.clinical_experience_dates_view_form').id, 'form')],
            'res_id': self.id,
            'target': 'new'
        })

        return action
    
    
    @api.model
    def create(self, values):
        res = super(ClinicalExperience, self).create(values)
        program_ids = self.env['program'].search([('company_id', '=', res.company_id.id)])
        for program_id in program_ids:
            program_id.create_update_program_experience_term()
        return res
    
class ClinicalExperienceDates(models.Model):
    _name = 'clinical.experience.dates'
    _description = 'Clinical Experience Dates'
    _rec_name = 'experience_id'
    _order = "year"
    
    experience_id = fields.Many2one(comodel_name='clinical.experience', string='Clinical Experience')
    company_id = fields.Many2one('res.company', related='experience_id.company_id', store=True)
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

    

class ClinicalExperienceSchedual(models.Model):
    _name = 'clinical.experience.schedual'
    _description = _('Clinical Experience Schedual')
    _order = "sequence"

    name = fields.Char(string='Term', compute='_compute_term_name', store=True,)
    experience_id = fields.Many2one(comodel_name='clinical.experience', string='Clinical Experience')
    sequence = fields.Char(related='experience_id.sequence', store=True)
    student_id = fields.Many2one(comodel_name='res.partner', string='Student')
    company_id = fields.Many2one('res.company', related='student_id.company_id')
    state = fields.Selection([
            ('not_taked', 'Not Taked'),
            ('taked', 'Taked'),
        ], string='Status', compute='_compute_student_experience_state')
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term',)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year')
    archive_create_date = fields.Datetime(
        string=_('Archive Create Date'),
        compute='_compute_experience_placement'
    )
    placement_status = fields.Selection([
            ('decline', 'Decline'),
            ('not_placed', 'Not Placed'),
            ('matched', 'Matched'),
            ('decline', 'Declined'),
            ('approved', 'Approved'),
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('completed', 'Completed'),
        ], compute='_compute_experience_placement', string='Placement Status')

    @api.depends('experience_id')
    def _compute_experience_placement(self):
        for rec in self:
            archive_id = self.env['archive'].search([('student_id', '=', rec.student_id.id), ('experience_id', '=', rec.experience_id.id)], limit=1, order="id desc")
            if archive_id:
                rec.archive_create_date = archive_id.create_date
                rec.placement_status = archive_id.placement_status
            else:
                rec.archive_create_date = False
                rec.placement_status = False
    
    @api.depends('experience_id', 'name')
    def _compute_student_experience_state(self):
        for rec in self:
            if self.env['archive'].search([('student_id', '=', rec.student_id.id), ('experience_id', '=', rec.experience_id.id), ('placement_status', 'in', ['confirmed', 'completed'])]):
                rec.state = 'taked'
            else:
                rec.state = 'not_taked'

    @api.depends('placement_term', 'year')
    def _compute_term_name(self):
        student_rec = self.env['res.partner']
        for rec in self:
            print(rec.placement_term, rec.year)
            if rec.placement_term and rec.year:
                rec.name = student_rec.convert_term_year(rec.placement_term, rec.year)
            else:
                rec.name = ''