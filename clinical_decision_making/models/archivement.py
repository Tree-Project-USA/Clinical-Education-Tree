# -*- coding: utf-8 -*-

from odoo import models, fields, api


SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(1999, 2500)]

class Archive(models.Model):
    _name = 'archive'
    _description = 'Archive Placement'
    _rec_name = 'facility_id'
    
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', )
    facility_id = fields.Many2one('medical.facility', string='Medical Facility', )
    date = fields.Date(string='Date',default=fields.Date.today(), )
    date_begin = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    offer_line_id = fields.Many2one(comodel_name='placement.offer.line', string="Offer line")
    offer_id = fields.Many2one(comodel_name='placement.offer', string="Offer")
    geographical_id = fields.Many2one(comodel_name='geographical', string='Geographical')
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    zip_code = fields.Char(related='geographical_id.zip_code')
    placement_type = fields.Selection([
        ('ice', 'ICE'),
        ('tce1', 'TCE1'),
        ('tce2', 'TCE2'),
    ], string='Type',)
    code = fields.Selection([
        ('op', 'OP'),
        ('ip', 'IP'),
    ], string='Code',)
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term',)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year',)
    
    
    _sql_constraints = [
        ('uniq_student_period', 'unique(student_id, placement_type)', 'The student period is already present. ')
    ]
    
 