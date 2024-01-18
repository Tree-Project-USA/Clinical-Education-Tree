# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError


SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]

class Archive(models.Model):
    _name = 'archive'
    _inherit = ['mail.thread']
    _description = 'Archive Placement'
    _rec_name = 'facility_id'
        
    studentid = fields.Char(related='student_id.studentid')
    student_id = fields.Many2one(comodel_name='res.partner', string='Student Name', tracking=True)
    first_name = fields.Char(related='student_id.first_name')
    last_name = fields.Char(related='student_id.last_name')
    facility_id = fields.Many2one('medical.facility', string='Facility', tracking=True)
    offer_id = fields.Many2one(comodel_name='placement.offer', string="Offer")
    request_id = fields.Many2one(comodel_name='placement.request', string="Placement Request")
    geographical_id = fields.Many2one(comodel_name='geographical', string='Facility Zip Code', tracking=True)
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    zip_code = fields.Char(related='geographical_id.zip_code')
    placement_type = fields.Selection([
        ('ice', 'ICE'),
        ('tce1', 'TCE1'),
        ('tce2', 'TCE2'),
    ], string='Clinical Experience Type', store=True, tracking=True)
    setting = fields.Selection([
        ('op', 'OP'),
        ('ip', 'IP'),
    ], string='Setting Type', tracking=True)
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term', compute='_compute_term_year', store=True, tracking=True)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year', compute='_compute_term_year', store=True, tracking=True)
    placement_status = fields.Selection([
        ('decline', 'Decline'),
        ('not_placed', 'Not Placed'),
        ('matched', 'Matched'),
        ('decline', 'Declined'),
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    ], default='matched', string='Placement Status', store=True, tracking=True)
    
    hardship_status = fields.Selection([
        ('approved', 'Approved'),
        ('not_approved', 'Not Approved'),
    ], string='Hardship Status', compute='_compute_hardship_status', store=True, precompute=True)
    archive_state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Term')
    offer_criteria = fields.Html(string='Offer Criteria')
    student_criteria = fields.Html(string='Student Criteria')
    match_state = fields.Selection([
        ('approve', 'Approved'),
        ('decline', 'Declined'),
    ], string='Match State', tracking=True)
    archive_offer_id = fields.Many2one('archive.offer', string='Archive Offer')
    is_show_student = fields.Boolean("Show to Student")
    ice_term = fields.Char(string='ICE Term', related='student_id.ice_term', store=True,)
    tce1_term = fields.Char(string='TCE1 Term', related='student_id.tce1_term', store=True,)
    tce2_term = fields.Char(string='TCE2 Term', related='student_id.tce2_term', store=True,)
    is_declined = fields.Boolean("Is Declined", tracking=True)
    
    def declined_student_offer(self):
        print(self.offer_id)
        if self.offer_id or self.archive_offer_id.offer_id:
            offer_id = self.offer_id or self.archive_offer_id.offer_id
            offer_id.write({
                'blocked_ids': [Command.link(self.student_id.id)]
                })
            self.is_declined = True
            if self.archive_offer_id:
                self.archive_offer_id.is_linked = False
                self.archive_offer_id.student_id = False
            self.action_decline()
            self.placement_status = 'decline'
        else:
            self.action_decline()
    
    def apply_student_offer(self):
        if self.offer_id or self.archive_offer_id.offer_id:
            offer_id = self.offer_id or self.archive_offer_id.offer_id
            offer_id.write({
                'blocked_ids': [Command.unlink(self.student_id.id)]
                })
        self.is_declined = False
        self.placement_status = 'not_placed'

    @api.constrains('student_id', 'placement_type', 'placement_status', 'setting')
    def _check_placement_status(self):
        for rec in self:
            comp_archive = self.env['archive'].search_count([('student_id', '=', rec.student_id.id), ('id', '!=', rec.id), ('placement_type', '=', rec.placement_type), ('placement_status', 'in', ['confirmed', 'completed'])]) and rec.placement_status in ['confirmed', 'completed']
            if comp_archive:
                raise ValidationError("Student (%s) is already Matching In (%s) for (%s)" % (rec.student_id.name, rec.facility_id.name,rec.placement_type))
    
    @api.constrains('student_id', 'placement_type', 'placement_status', 'setting')
    def _check_placement_status_SSSSS(self):
        for rec in self:
            comp_ice = self.env['archive'].search_count([('student_id', '=', rec.student_id.id), ('placement_type', '=', 'ice'), ('placement_status', 'in', ['completed', 'confirmed'])])
            comp_tce1 = self.env['archive'].search_count([('student_id', '=', rec.student_id.id), ('placement_type', '=', 'tce1'), ('placement_status', 'in', ['completed', 'confirmed'])])
            comp_tce2 = self.env['archive'].search_count([('student_id', '=', rec.student_id.id), ('placement_type', '=', 'tce2'), ('placement_status', 'in', ['completed', 'confirmed'])])
            if comp_tce2:
                if comp_tce1:
                    pass
                else:
                    raise ValidationError("Student %s should take TCE 1 term before TCE 2" % (rec.student_id.name))
            if comp_tce1:
                if comp_ice:
                    pass
                else:
                    raise ValidationError("Student %s should not take TCE term before ICE" % (rec.student_id.name))
            
            comp_all = self.env['archive'].search_count([('student_id', '=', rec.student_id.id), ('placement_status', 'in', ['completed', 'confirmed'])])
            if comp_all >= 3:
                count_ip = self.env['archive'].search_count([('student_id', '=', rec.student_id.id), ('placement_status', 'in', ['completed', 'confirmed']), ('setting', '=', 'ip')])
                if not count_ip:
                    raise ValidationError("Student %s must have at least one setting type IP" % (rec.student_id.name))
            count_ip = self.env['archive'].search_count([('student_id', '=', rec.student_id.id), ('placement_status', 'in', ['completed', 'confirmed']), ('setting', '=', 'ip')])
            if count_ip > 1:
                raise ValidationError("Student %s already take  IP Setting" % (rec.student_id.name))
        
    # @api.constrains('student_id','placement_type', 'facility_id', 'placement_status', 'setting')
    # def _check_placement_type(self):
    #     for rec in self:
    #         if self.env['archive'].search_count([('student_id', '=', rec.student_id.id), ('placement_status', 'in', ['confirmed', 'completed']), ('id', '!=', rec.id), ('setting', '=', 'ip')]):
    #             raise ValidationError(_("Student %s already take  IP Setting" % (rec.student_id.name)))
            
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
            
    
    def write(self, vals):
        print(vals)
        res = super(Archive, self).write(vals)
        if 'placement_status' in vals:
            for rec in self:
                if rec.placement_status == 'confirmed':
                    self.search([('id', '!=', self.id), ('student_id', '=', self.student_id.id), ('placement_type', '=', self.placement_type), ('placement_term', '=', self.placement_term)]).write({
                        'placement_status': 'not_placed'
                    })
                    
                if rec.placement_status == 'not_placed':
                    rec.unlink_offer()
        return res
    
    def convert_abbr_to_term_year(self, term_year):
        term_abbr = term_year[:2]
        year_abbr = term_year[2:]

        term = ""
        if term_abbr.upper() == "FA":
            term = "Fall"
        elif term_abbr.upper() == "SP":
            term = "Spring"
        elif term_abbr.upper() == "SU":
            term = "Summer"

        year = "20" + year_abbr

        return term, int(year)

    @api.depends('student_id', 'placement_type')
    def _compute_term_year(self):
        for rec in self:
            if rec.student_id and rec.placement_type:
                if rec.placement_type == "ice" and rec.student_id.ice_term:
                    term,year = rec.convert_abbr_to_term_year(rec.student_id.ice_term)
                    rec.year = str(year)
                    rec.placement_term = term.lower()
                elif rec.placement_type == "tce1" and rec.student_id.tce1_term:
                    term,year = rec.convert_abbr_to_term_year(rec.student_id.tce1_term)
                    rec.year = str(year)
                    rec.placement_term = term.lower()
                elif rec.placement_type == "tce2" and rec.student_id.tce2_term:
                    term,year = rec.convert_abbr_to_term_year(rec.student_id.tce2_term)
                    rec.year = str(year)
                    rec.placement_term = term.lower()
            
    def action_approve(self):
        self.write({
         'match_state': 'approve',
         'placement_status': 'approved'
        })
        if self.request_id:
            self.request_id._onchange_apply_criteria()
        
        
    def action_decline(self):
        self.write({
         'match_state': 'decline',
        })
        self.unlink_offer()
        self.placement_status = 'not_placed'
        if self.request_id:
            self.request_id._onchange_apply_criteria()
    
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
    
    def confirm_placement_status(self):
        print(       self.search([('id', '!=', self.id), ('student_id', '=', self.student_id.id), ('placement_type', '=', self.placement_type), ('placement_term', '=', self.placement_term)]))
        print(       self.search([('id', '!=', self.id), ('student_id', '=', self.student_id.id), ('placement_type', '=', self.placement_type), ('placement_term', '=', self.placement_term)]))
        print(       self.search([('id', '!=', self.id), ('student_id', '=', self.student_id.id), ('placement_type', '=', self.placement_type), ('placement_term', '=', self.placement_term)]))
        print(       self.search([('id', '!=', self.id), ('student_id', '=', self.student_id.id), ('placement_type', '=', self.placement_type), ('placement_term', '=', self.placement_term)]))
        self.search([('id', '!=', self.id), ('student_id', '=', self.student_id.id), ('placement_type', '=', self.placement_type), ('placement_term', '=', self.placement_term)]).write({
            'placement_status': 'not_placed'
        })

    
    def action_open_archive_log(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.archive_action')
        action['context'] = {'create': False, 'delete': False, 'edit': False}
        action.update({
            'view_mode': 'form',
            'view_id': self.env.ref('clinical_decision_making.archive_wizard_view_form').id,
            'views': [(self.env.ref('clinical_decision_making.archive_wizard_view_form').id, 'form')],
            'res_id': self.id,
            # 'target': 'inline'
        })
        return action