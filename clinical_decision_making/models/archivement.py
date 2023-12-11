# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Archive(models.Model):
    _name = 'archive'
    _description = 'Archive Placement'
    _rec_name = 'facility_id'
    
    student_id = fields.Many2one(comodel_name='res.partner', string='Student', readonly=True)
    facility_id = fields.Many2one('medical.facility', string='Medical Facility', readonly=True)
    date = fields.Date(string='Date',default=fields.Date.today(), readonly=True)
    date_begin = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    offer_line_id = fields.Many2one(comodel_name='placement.offer.line', string="Setting Intership", required=True)
    offer_id = fields.Many2one(comodel_name='placement.offer', realted='offer_line_id.offer_id')
    geographical_id = fields.Many2one(comodel_name='geographical', string='Geographical')
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    zip_code = fields.Char(related='geographical_id.zip_code')
    placement_type = fields.Selection([
        ('ice', 'ICE'),
        ('tce1', 'TCE1'),
        ('tce2', 'TCE2'),
    ], string='Type', required=True)
    code = fields.Selection([
        ('op', 'OP'),
        ('ip', 'IP'),
    ], string='Code', required=True)
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term', required=True)
    
    _sql_constraints = [
        ('uniq_student_period', 'unique(student_id, placement_type)', 'The student period is already present. ')
    ]
    
 