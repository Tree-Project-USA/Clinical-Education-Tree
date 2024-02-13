# -*- coding: utf-8 -*-

from odoo import models, fields, api

SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]

class ArchiveOffer(models.Model):
    _name = 'archive.offer'
    _description = 'Archive Offer'
    _rec_name = 'department_id'
    
    active = fields.Boolean(string='Active', default=True)
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', check_company=True)
    is_linked = fields.Boolean('is Joined', default=False, readonly=True)
    department_id = fields.Many2one(comodel_name='facility.department' , string='Department', check_company=True)
    facility_id = fields.Many2one(comodel_name='medical.facility', related='department_id.facility_id', store=True,)
    offer_id = fields.Many2one(comodel_name='placement.offer', string='Offer', check_company=True)
    offer_line_id = fields.Many2one(comodel_name='placement.offer.line', string='Line', check_company=True)
    setting = fields.Selection(related='offer_line_id.setting', store=True)
    experience_id = fields.Many2one(comodel_name='clinical.experience', string='Clinical Experience', domain="[('company_id', '=', company_id)]", required=True, check_company=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term', required=True)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year', required=True)
    term = fields.Char(string='Term', compute='_compute_term', store=True)
    
    @api.depends('placement_term', 'year', 'offer_id')
    def _compute_term(self):
        for rec in self:
            if rec.year and rec.placement_term:
                rec.term = self.env['placement.request'].convert_term_year(rec.placement_term, rec.year)
            else:
                rec.term = ''