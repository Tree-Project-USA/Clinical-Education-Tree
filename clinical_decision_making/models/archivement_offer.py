# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ArchiveOffer(models.Model):
    _name = 'archive.offer'
    _description = 'Archive Offer'
    _rec_name = 'facility_id'
    
    student_id = fields.Many2one(comodel_name='res.partner', string='Student')
    is_linked = fields.Boolean('is Joined', default=False, readonly=True)
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Facility')
    offer_id = fields.Many2one(comodel_name='placement.offer', string='Offer')
    offer_line_id = fields.Many2one(comodel_name='placement.offer.line', string='Line')
    setting = fields.Selection(related='offer_line_id.setting', store=True)
    placement_type = fields.Selection(related='offer_id.placement_type', store=True)
    placement_term = fields.Selection(related='offer_id.placement_term', store=True)
    year = fields.Selection(related='offer_id.year', store=True)
    

    