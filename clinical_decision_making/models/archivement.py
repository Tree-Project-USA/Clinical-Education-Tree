# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError


SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]

class Archive(models.Model):
    _name = 'archive'
    _inherit = ['mail.thread']
    _description = 'Archive Placement'
    _rec_name = 'department_id'
        
    active = fields.Boolean(string='Active', default=True)
    student_id = fields.Many2one(comodel_name='res.partner', string='Student Name', tracking=True)
    first_name = fields.Char(related='student_id.first_name')
    last_name = fields.Char(related='student_id.last_name')
    facility_id = fields.Many2one('medical.facility', string='Clinical Site', related='department_id.facility_id', readonly=True)
    offer_id = fields.Many2one(comodel_name='placement.offer', string="Offer")
    request_id = fields.Many2one(comodel_name='placement.request', string="Placement Request")
    geographical_id = fields.Many2one(comodel_name='geographical', string='Clinical Site Zip Code', tracking=True)
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    zip_code = fields.Char(related='geographical_id.zip_code')
    experience_id = fields.Many2one(comodel_name='clinical.experience', string='Clinical Experience', required=True, tracking=True)
    company_id = fields.Many2one(related='student_id.company_id', store=True)
    setting = fields.Selection([('op', 'OP'),('ip', 'IP')], string='Setting Type', tracking=True)
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
    archive_offer_id = fields.Many2one('archive.offer', string='Archive Offer', domain="[('student_id', '=', False), ('term', '=', term)]")
    is_show_student = fields.Boolean("Show to Student")

    is_declined = fields.Boolean("Is Declined", tracking=True)
    department_id = fields.Many2one(comodel_name='facility.department' , related='archive_offer_id.department_id', store=True,  readonly=False)
    term = fields.Char(string='Term', compute='_compute_term', store=True)
    main_offer_student_id = fields.Many2one(comodel_name='res.partner', string='Main offer Student')
    is_show_portal = fields.Boolean(string='Show in Portal')
    
    @api.depends('placement_term', 'year')
    def _compute_term(self):
        for rec in self:
            if rec.year and rec.placement_term:
                rec.term = self.env['placement.request'].convert_term_year(rec.placement_term, rec.year)
            else:
                rec.term = ''
    
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

    @api.constrains('student_id', 'experience_id', 'placement_status', 'setting')
    def _check_placement_status(self):
        for rec in self:
            comp_archive = self.env['archive'].search_count([('student_id', '=', rec.student_id.id), ('id', '!=', rec.id), ('experience_id', '=', rec.experience_id.id), ('placement_status', 'in', ['confirmed', 'completed'])]) and rec.placement_status in ['confirmed', 'completed']
            if comp_archive:
                raise ValidationError("Student (%s) is already Matching In (%s) for (%s)" % (rec.student_id.name, rec.facility_id.name, rec.experience_id.name))
    

    def write(self, vals):
        res = super(Archive, self).write(vals)
        if 'placement_status' in vals:
            for rec in self:
                if rec.placement_status == 'confirmed':
                    self.search([('id', '!=', self.id), ('student_id', '=', self.student_id.id), ('experience_id', '=', self.experience_id.id), ('placement_term', '=', self.placement_term)]).write({
                        'placement_status': 'not_placed'
                    })
                    ptse_1_survey = rec.experience_id.ptse_1_survey    
                    ptse_2_survey = rec.experience_id.ptse_2_survey
                    user_input_1 = ptse_1_survey.mapped('user_input_ids').search([
                        ('partner_id', '=', rec.student_id.id),
                        ('state', '=', 'done'),
                        ('survey_id', '=', ptse_1_survey.id)
                        ])
                    user_input_2 = ptse_2_survey.mapped('user_input_ids').search([
                        ('partner_id', '=', rec.student_id.id),
                        ('state', '=', 'done'),
                        ('survey_id', '=', ptse_2_survey.id)
                        ])
                    self.env["post.plcement.management"].sudo().create({
                       'archive_id': rec.id,
                       'student_id': rec.student_id.id,
                       'facility_id': rec.department_id.facility_id.id,
                       'experience_id': rec.experience_id.id,
                       'year': rec.year if rec.year else False,
                       'placement_term': rec.placement_term if rec.placement_term else False,
                       'ptse_1': user_input_1.id if user_input_1 else False,
                       'ptse_2': user_input_2.id if user_input_2 else False,
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

    @api.depends('student_id', 'experience_id')
    def _compute_term_year(self):
        for rec in self:
            if rec.student_id and rec.experience_id:
                schedual_id = rec.student_id.get_student_schedual(rec.experience_id.id)
                rec.year = schedual_id.year
                rec.placement_term = schedual_id.placement_term

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
        action = self.env.ref('clinical_decision_making.student_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.student_id.ids)]
        action.update({
            'view_mode': 'form',
            'res_id': self.student_id.id,
            'view_id': self.env.ref('clinical_decision_making.student_view_form').id,
            'views': [(self.env.ref('clinical_decision_making.student_view_form').id, 'form')],
        })
        return action
    
    def confirm_placement_status(self):
        self.search([('id', '!=', self.id), ('student_id', '=', self.student_id.id), ('experience_id', '=', self.experience_id.id), ('placement_term', '=', self.placement_term)]).write({
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
    
    def _get_ptse_survey(self, type_ptse):
        post_plcement = self.env["post.plcement.management"].search([
            ('facility_id', '=', self.facility_id.id),
            ('experience_id', '=', self.experience_id.id)
            ])
        if type_ptse == 'ptse_1_survey':
            ptse_1_survey =  post_plcement.experience_id.ptse_1_survey
            return {'ptse_1_survey': ptse_1_survey, 'user_input': post_plcement.ptse_1}
        else:
            ptse_2_survey =  post_plcement.experience_id.ptse_2_survey
            return {'ptse_2_survey': ptse_2_survey, 'user_input': post_plcement.ptse_2}
            