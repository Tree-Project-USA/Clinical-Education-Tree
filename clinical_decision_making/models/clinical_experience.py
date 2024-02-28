# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]


class ClinicalExperience(models.Model):
    _name = 'clinical.experience'
    _description = _('Clinical Experience')
    _order = "sequence"

    active = fields.Boolean(string='Status')
    name = fields.Char(string='Clinical Experience Name')
    sequence = fields.Char(
        'Sequence', default=lambda self: self.env['ir.sequence'].next_by_code('clinical.experience'), company_dependent=True)
    company_id = fields.Many2one('res.company', string='Program', default=lambda self: self.env.user.company_id)
    ptse_2_survey = fields.Many2one('survey.survey', string="PTSE 2 Survey", domain=[('ptse_type', '=', 'ptse_2')])
    ptse_1_survey = fields.Many2one('survey.survey', string="PTSE 1 Survey", domain=[('ptse_type', '=', 'ptse_1')])
    
    
    @api.model
    def create(self, values):
        res = super(ClinicalExperience, self).create(values)
        program_ids = self.env['program'].search([('company_id', '=', res.company_id.id)])
        for program_id in program_ids:
            program_id.create_update_program_experience_term()
        return res
    

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