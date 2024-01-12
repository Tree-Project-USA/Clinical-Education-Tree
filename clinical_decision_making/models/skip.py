# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]

class Skip(models.Model):
    _name = 'skip'
    _description = "Student Skip Term"

    student_id = fields.Many2one(comodel_name='res.partner', string='Student', ondelete='cascade')
    term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term')
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year')
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
    def _check_student_skipped_terms(self):
        for rec in self:
            existing_skip = self.env['skip'].search([
                ('id', '!=', rec.id),
                ('student_id', '=', rec.student_id.id),
                ('term', '=', rec.term),
                ('year', '=', rec.year)
            ])
            if existing_skip:
                term = rec.student_id.convert_term_year(rec.term, rec.year)
                raise ValidationError(_("Student %s has already skipped the %s term") % (rec.student_id.name, term))