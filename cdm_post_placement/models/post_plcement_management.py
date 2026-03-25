# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]


class PostPlcement(models.Model):
    _name = 'plcement.management'

class PostPlcement(models.Model):
    _name = 'post.plcement.management'
    _description = _('Post Plcement management')

    archive_id = fields.Many2one(comodel_name='archive', string='archive', ondelete='cascade')
    student_id = fields.Many2one(comodel_name='res.partner', string='Student',domain=[('is_student', '=', True)])
    facility_id = fields.Many2one('medical.facility', string='Clinical Site', readonly=True)
    experience_id = fields.Many2one(comodel_name='clinical.experience', string='Clinical Experience', domain="[('company_id', '=', company_id)]", required=True, check_company=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year', default='2000')
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ], string='Term')
    ptse_2 = fields.Many2one('survey.user_input', string="PTSE 2")  
    ptse_1 = fields.Many2one('survey.user_input', string="PTSE 1")  
    ptse_3_id = fields.Many2one('ci.ptse')
    ci_id = fields.Many2one(related='ptse_3_id.ci_id', store=True)
    ptse_3 = fields.Binary(related='ptse_3_id.ptse_3', store=True, string="PTSE 3")
    
   