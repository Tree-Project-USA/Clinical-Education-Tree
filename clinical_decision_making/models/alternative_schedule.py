# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]

class AlternativeSchedule(models.Model):
    _name = 'alternative.schedule'
    _description = "Student Alternative Schedule"

    student_id = fields.Many2one(comodel_name='res.partner', string='Student', ondelete='cascade')
    term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term Skipped', required=True)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year Skipped', required=True)
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)
    state = fields.Selection(
        string=_('State'),
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ],
        default='draft'
    )
    
    def action_confirm(self):
        self.write({
            'state': 'confirmed'
        })
        
    def action_draft(self):
        self.write({
            'state': 'draft'
        })
    
    @api.constrains('student_id', 'term', 'year')
    def _check_student_alternative_schedule(self):
        for rec in self:
            existing_alternative_schedule = self.env['alternative.schedule'].search([
                ('id', '!=', rec.id),
                ('student_id', '=', rec.student_id.id),
                ('term', '=', rec.term),
                ('year', '=', rec.year)
            ])
            if existing_alternative_schedule:
                term = rec.student_id.convert_term_year(rec.term, rec.year)
                raise ValidationError(_("Student %s has already alternative schedule for %s term. ") % (rec.student_id.name, term))
    
    def alternative_schedule_student_term_action(self):
        self.ensure_one()
        if self.student_id:
            return self.student_id.action_view_alternative_schedule()
