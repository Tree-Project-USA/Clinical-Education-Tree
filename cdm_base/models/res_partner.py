# -*- coding: utf-8 -*-
import requests
import json
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_student = fields.Boolean(string='Is Student', default=False)
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id, required=True)
    name = fields.Char(string='Name', compute='_compute_name', store=True, default='')
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    
    campus_id = fields.Many2one(comodel_name='student.campus', string='Campus')
    program_id = fields.Many2one(comodel_name='program', string='Program Duration')
    program_type = fields.Char(string='Program Type', default='DPT')
    
    start_term_type = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Start Term')
    start_year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Start Year')
    
    home_address = fields.Char(string='Home Address')
    personal_phone = fields.Char(string='Personal Phone')
    personal_email_address = fields.Char(string='Personal Email Address')
    graduation_term = fields.Char(string='Graduation Term/Year')
    cohort_label = fields.Char(string='Cohort')
    
    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for record in self:
            if record.first_name or record.last_name:
                record.name = f"{record.first_name if record.first_name else ''} {record.last_name if record.last_name else ''}" 

    @api.constrains('email')
    def validate_mail(self):
        if self.email:
            if not re.match('^[_A-Za-z0-9-]+(\.[_A-Za-z0-9-]+)*@[_A-Za-z0-9-]+(\.[_A-Za-z0-9-]+)*(\.[A-Za-z]{2,4})$', self.email):
                raise ValidationError(_('The personal email address must be valid ( example@example.com )'))

    def action_send_portal_invitation_bulk(self):
        partners = self.search([('email', '!=', False), ('is_student', '=', True), ('user_ids', '=', False)])
        for partner in partners:
            partner.with_context(signup_force_type_new=True)._send_signup_email()

    def get_student_schedual(self, experience_id):
        self.ensure_one()
        return self.env['clinical.experience.schedual'].search([
            ('student_id', '=', self.id),
            ('experience_id', '=', experience_id)
        ], limit=1)

    @api.model
    def convert_term_year(self, term, year):
        if not term or not year:
            return ""
        term_abbr = {
            "fall": "FA",
            "spring": "SP",
            "summer": "SU"
        }.get(term.lower(), "")
        year_abbr = str(year)[-2:]
        return term_abbr + year_abbr
