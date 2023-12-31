# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(1999, 2500)]

class Archive(models.Model):
    _name = 'archive'
    _description = 'Archive Placement'
    _rec_name = 'facility_id'
    
    student_id = fields.Many2one(comodel_name='res.partner', string='Student Name')
    first_name = fields.Char(related='student_id.first_name')
    last_name = fields.Char(related='student_id.last_name')
    facility_id = fields.Many2one('medical.facility', string='Matching Facility')
    offer_id = fields.Many2one(comodel_name='placement.offer', string="Offer")
    request_id = fields.Many2one(comodel_name='placement.request', string="Placement Request")
    geographical_id = fields.Many2one(comodel_name='geographical', string='Facility Zip Code')
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    zip_code = fields.Char(related='geographical_id.zip_code')
    placement_type = fields.Selection([
        ('ice', 'ICE'),
        ('tce1', 'TCE1'),
        ('tce2', 'TCE2'),
    ], string='Clinical Experience Type', store=True)
    setting = fields.Selection([
        ('op', 'OP'),
        ('ip', 'IP'),
    ], string='Setting',)
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Start Term', store=True)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Start Year', store=True)
    placement_status = fields.Selection([
        ('not_placed', 'Not Placed'),
        ('matched', 'Matched'),
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    ], default='matched', string='placement status', store=True)
    
    hardship_status = fields.Selection([
        ('approved', 'Approved'),
        ('not_approved', 'Not Approved'),
    ], string='Hardship Status', compute='_compute_hardship_status', store=True, precompute=True)
    archive_state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Term',)
    criteria = fields.Html(string='Criteria')
    match_state = fields.Selection([
        ('approve', 'Approved'),
        ('decline', 'Declined'),
    ], string='Match State',)
    archive_offer_id = fields.Many2one('archive.offer', string='Archive Offer')
    
    @api.constrains('placement_status')
    def _check_placement_status(self):
        for rec in self:
            if self.env['archive'].search([('student_id', '=', rec.student_id.id), ('placement_type', '=', rec.placement_type), ('placement_status', 'in', ['approved', 'completed', 'pending']), ('id', '!=', rec.id)]):
                raise ValidationError("Student (%s) is already Matching (%s) for (%s)" % (rec.student_id.name, rec.facility_id.name,rec.placement_type))
                
        
    @api.constrains('placement_type', 'facility_id')
    def _check_placement_type(self):
        for rec in self:
            print('_check_placement_type', rec)
            # if self.env['archive'].search([('student_id', '=', rec.student_id.id), ('facility_id', '=', rec.facility_id.id), ('placement_status', 'in', ['approved', 'completed', 'pending']), ('id', '!=', rec.id)]) and not rec.student_id.is_with_hardship:
            #     raise ValidationError("Student %s is already placed to %s facility" % (rec.student_id.name, rec.facility_id.name))    
            
            # if self.env['archive'].search([('student_id', '=', rec.student_id.id), ('placement_type', '=', rec.placement_type), ('placement_status', 'in', ['approved', 'completed']), ('id', '!=', rec.id)]):
            #     raise ValidationError("Student %s is already taken in %s term before" % (rec.student_id.name, rec.placement_type))
            
            # if rec.placement_type == 'ice':
            #     archive_id = self.env['archive'].search([('student_id', '=', rec.student_id.id), ('placement_type', '=', 'ice'), ('placement_status', 'in', ['approved', 'completed']), ('id', '!=', rec.id)])
            #     if archive_id:
            #         raise ValidationError("Term ICE Pass")
            
            # if rec.placement_type == 'tce1':
            #     archive_id = self.env['archive'].search([('student_id', '=', rec.student_id.id), ('placement_type', '=', 'ice'), ('placement_status', 'in', ['approved', 'completed']), ('id', '!=', rec.id)])
            #     if not archive_id:
            #         raise ValidationError("Student %s is Shuld Take ICE term before TCE1" % (rec.student_id.name))
            
            # if rec.placement_type == 'tce2':
            #     archive_id = self.env['archive'].search([('student_id', '=', rec.student_id.id), ('placement_type', '=', 'tce1'), ('placement_status', 'in', ['approved', 'completed']), ('id', '!=', rec.id)])
            #     if not archive_id:
            #         raise ValidationError("Student %s is Shuld Take TCE1 term before TCE2" % (rec.student_id.name))
            
    def action_approve(self):
        self.write({
         'match_state': 'approve',
        })
        
    def action_decline(self):
        self.write({
         'match_state': 'decline',
        })
        self.unlink_offer()
    
    @api.depends('student_id', 'student_id.hardship_ids', 'student_id.hardship_ids.state')
    def _compute_hardship_status(self):
        for rec in self:
            if rec.archive_state == 'draft':
                hardship_id = rec.student_id.hardship_ids
                if hardship_id:
                    rec.hardship_status = 'approved' if hardship_id.state == 'confirm' else 'not_approved'
                else:
                    rec.hardship_status = False
 
    def unlink_offer(self):
        if self.archive_offer_id:
            self.archive_offer_id.is_linked = False
            self.archive_offer_id.student_id = False
        self.placement_status = 'not_placed'
            
    def action_view_student(self):
        action = self.env.ref('clinical_decision_making.student_action').read()[0]
        action['domain'] = [('id', 'in', self.student_id.ids)]
        action.update({
            'view_mode': 'form',
            'res_id': self.student_id.id,
            'view_id': self.env.ref('clinical_decision_making.student_view_form').id,
            'views': [(self.env.ref('clinical_decision_making.student_view_form').id, 'form')],
        })
        return action