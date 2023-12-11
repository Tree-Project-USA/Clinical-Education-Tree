# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PlacementRequest(models.Model):
    _name = 'placement.request'
    _inherit = ['mail.thread']
    _description = 'Placement Request'
    _rec_name = 'name'
    
    name = fields.Char(string='Test')
    
    student_ids = fields.Many2many(comodel_name='res.partner', string='Students', compute='_filter_records', store=True,)
    line_ids = fields.Many2many(comodel_name='placement.offer.line', string='offers', compute='_filter_records', store=True,)
    facility_ids = fields.Many2many('medical.facility', string='Medical Facilities', compute='_filter_records', store=True,)
    
    student_count = fields.Integer(compute='_compute_count')
    line_count = fields.Integer(compute='_compute_count')
    facility_count = fields.Integer(compute='_compute_count')
    
    @api.depends('student_ids', 'line_ids', 'facility_ids')
    def _compute_count(self):
        for request in self:
            request.student_count = len(request.student_ids)
            request.line_count = len(request.line_ids)
            request.facility_count = len(request.facility_ids)
            
    # Filters
    placement_type = fields.Selection([
        ('ice', 'ICE'),
        ('tce1', 'TCE1'),
        ('tce2', 'TCE2'),
    ], string='Type', required=True)
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term', required=True)
    
    
    
    filter_by_hardship = fields.Boolean(string='Filter by Hardship')
    
    filter_by_offer = fields.Boolean(string='Filter by Offer')
    placement_offer_id = fields.Many2one(comodel_name='placement.offer', string='Offer')
    
    filter_by_program = fields.Boolean(string='Filter by Progrm')
    program_id = fields.Many2one(comodel_name='program', string='Program')
    
    filter_by_student = fields.Boolean(string='Filter by Student')
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', domain=[('is_student', '=', True)])
    
    filter_by_facility = fields.Boolean(string='Filter by Facility')
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Facility')
    
    
    @api.depends('placement_type', 'placement_term', 'filter_by_hardship', 'filter_by_offer', 'placement_offer_id', 'filter_by_program', 'program_id', 'filter_by_student', 'student_id', 'filter_by_facility', 'facility_id')
    def _compute_filtered_fields(self):
        for record in self:
            students = record._get_available_students()
            record.student_ids = students.ids if students else False

            lines = record._get_available_lines()
            record.line_ids = lines.ids if lines else False

            facilities = record._get_available_facilities()
            record.facility_ids = facilities.ids if facilities else False
    
    def _get_available_students(self):
        domain = []
        if self.placement_type:
            domain.append(('placement_type', '=', self.placement_type))
        if self.placement_term:
            domain.append(('placement_term', '=', self.placement_term))
        if self.filter_by_offer and self.placement_offer_id:
            domain.append(('placement_offer_id', '=', self.placement_offer_id.id))
        if self.filter_by_program and self.program_id:
            domain.append(('program_id', '=', self.program_id.id))
        if self.filter_by_student and self.student_id:
            domain.append(('student_id', '=', self.student_id.id))
        if self.filter_by_facility and self.facility_id:
            domain.append(('facility_id', '=', self.facility_id.id))
        if self.filter_by_hardship:
            domain.append(('hardship', '=', True))
        
        return self.env['res.partner'].search(domain)
    
    def _get_available_lines(self):
        domain = []
        if self.placement_type:
            domain.append(('placement_type', '=', self.placement_type))
        if self.placement_term:
            domain.append(('placement_term', '=', self.placement_term))
        if self.filter_by_offer and self.placement_offer_id:
            domain.append(('placement_offer_id', '=', self.placement_offer_id.id))
        if self.filter_by_program and self.program_id:
            domain.append(('program_id', '=', self.program_id.id))
        if self.filter_by_student and self.student_id:
            domain.append(('student_id', '=', self.student_id.id))
        if self.filter_by_facility and self.facility_id:
            domain.append(('facility_id', '=', self.facility_id.id))
        if self.filter_by_hardship:
            domain.append(('hardship', '=', True))
        
        return self.env['placement.offer.line'].search(domain)
    
    def _get_available_facilities(self):
        domain = []
        if self.placement_type:
            domain.append(('placement_type', '=', self.placement_type))
        if self.placement_term:
            domain.append(('placement_term', '=', self.placement_term))
        if self.filter_by_offer and self.placement_offer_id:
            domain.append(('placement_offer_id', '=', self.placement_offer_id.id))
        if self.filter_by_program and self.program_id:
            domain.append(('program_id', '=', self.program_id.id))
        if self.filter_by_student and self.student_id:
            domain.append(('student_id', '=', self.student_id.id))
        if self.filter_by_facility and self.facility_id:
            domain.append(('facility_id', '=', self.facility_id.id))
        if self.filter_by_hardship:
            domain.append(('hardship', '=', True))
        
        return self.env['medical.facility'].search(domain)
            

    @api.onchange('filter_by_offer')
    def _onchange_filter_by_offer(self):
        if not self.filter_by_offer:
            self.placement_offer_id = False
    
    @api.onchange('filter_by_program')
    def _onchange_filter_by_program(self):
        if not self.filter_by_program:
            self.program_id = False
    
    @api.onchange('filter_by_student')
    def _onchange_filter_by_student(self):
        if not self.filter_by_student:
            self.student_id = False
    
    @api.onchange('filter_by_facility')
    def _onchange_filter_by_facility(self):
        if not self.filter_by_facility:
            self.facility_id = False
    
    
    def action_view_students(self):
        action = self.env.ref('clinical_decision_making.student_action').read()[0]
        action['domain'] = [('id', 'in', self.student_ids.ids)]
        return action
    
    def action_view_lines(self):...
        # action = self.env.ref('clinical_decision_making.action_placement_offer_line').read()[0]
        # action['domain'] = [('id', 'in', self.line_ids.ids)]
        # return action
    
    def action_view_facilities(self):
        action = self.env.ref('clinical_decision_making.medical_facility_action').read()[0]
        action['domain'] = [('id', 'in', self.facility_ids.ids)]
        return action