# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]


class CIPtse(models.Model):
    _name = 'ci.ptse'
    _description = _('CI PTSE 3')
    _rec_name = 'sequence'
    _order = 'sequence'

    facility_id = fields.Many2one(comodel_name='medical.facility', string='Clinical Site', ondelete='cascade')
    archive_id = fields.Many2one(comodel_name='archive', string='Archive', ondelete='cascade', readonly=False)
    ci_id = fields.Many2one(comodel_name='res.partner', string='CI',domain=[('is_ci', '=', True)])
    ci_details_status = fields.Selection(related='ci_id.ci_details_status', store=True)
    student_id = fields.Many2one(comodel_name='res.partner', string='Student',domain=[('is_student', '=', True)])
    company_id = fields.Many2one(related='student_id.company_id')
    campus = fields.Char(related='student_id.campus', readonly=False)
    home_address = fields.Char(related='student_id.home_address', string="Address")
    name_clinical_education_site = fields.Char(string='Name of Clinical Education Site')
    city = fields.Char(string='City')
    state = fields.Char(string='state')
    clinical_experience_number = fields.Char(string='Clinical Experience Number')
    clinical_experience_dates = fields.Date(string='Clinical Experience dates')
    setting = fields.Selection(related='archive_id.setting')
    placement_term = fields.Selection(related='archive_id.placement_term')
    year = fields.Selection(related='archive_id.year')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_ci', "CI")], default=False, help="Technical field for UX purpose.")
    stage_type = fields.Selection([
        ('ci_details', "CI Details"),
        ('ptse3', "PTSE 3")],
        default='ci_details')
    sequence = fields.Char(string='Sequence', index=True,  default=_('New'))
    student_signature = fields.Binary(string="Student Signature")
    student_signature_date = fields.Date(string="Student Signature Date")
    ci_signature = fields.Binary(string="CI Signature")
    ci_signature_date = fields.Date(string="CI Signature Date")
    ptse_3 = fields.Binary(string="PTES 3")
    
    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code('post.plcement.management') or _('New')
        return super(CIPtse, self).create(vals)

    
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (dict(self._fields['stage_type'].selection).get(self.stage_type))