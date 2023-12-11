# -*- coding: utf-8 -*-

from odoo import models, fields, api


def SELECTION_YEAR_RANGE():
    return [(str(i),str(i)) for i in range(1999, 2500)]
class PlacementOffer(models.Model):
    _name = 'placement.offer'
    _inherit = ['mail.thread']
    _description = 'Placement Offer'
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True, index=True, copy=False, default='New')
    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Urgent')], 'Priority', default='0', index=True)
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Medical Facility')
    line_ids = fields.One2many(comodel_name='placement.offer.line', inverse_name='offer_id', string='Placement Lines')
    student_ids = fields.Many2many(comodel_name='res.partner', string='Students',domain=[('is_student', '=', True)], compute='_compute_offer_student_ids')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('post', 'Placement Intership'),
        ], string='Status', default='draft')
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
        
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year', required=True)
    date = fields.Date(string='Year', required=True)
    
    @api.depends('line_ids')
    def _compute_offer_student_ids(self):
        for rec in self:
            rec.student_ids = rec.line_ids.mapped('student_ids')


class PlacementOfferLine(models.Model):
    _name = 'placement.offer.line'

    name = fields.Char(string='Name')
    offer_id = fields.Many2one(comodel_name='placement.offer', string='Parent Offer')
    parent_state = fields.Selection(related='offer_id.state')
    placement_type = fields.Selection(related='offer_id.placement_type')
    placement_term = fields.Selection(related='offer_id.placement_term')
    code = fields.Selection(string='Code', selection=[('ip', 'IP'), ('op', 'OP')], default='op', required=True)
    student_count = fields.Integer(string='Number of students')
    avalible_stu_count = fields.Integer(string='Avalible Student', compute='_compute_avalible_stu_count', store=False)
    student_ids = fields.Many2many(comodel_name='res.partner', string='Students',domain=[('is_student', '=', True)])
    status = fields.Selection([
            ('Pending', 'Watting for Confirmation'),
            ('Confirmed', 'Confirmed'),
            ('not_placed', 'Not Placed'),
        ], string='Status', default='Pending')
    
    @api.depends('student_count')
    def _compute_avalible_stu_count(self):
        for rec in self:
            student_count = len(rec.student_ids)
            rec.avalible_stu_count = 0 if student_count - student_count < 0 else student_count - student_count
    
    