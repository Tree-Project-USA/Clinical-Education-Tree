# -*- coding: utf-8 -*-
from lxml import etree
import json
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(1999, 2500)]
class PlacementOffer(models.Model):
    _name = 'placement.offer'
    _inherit = ['mail.thread']
    _description = 'Placement Offer'
    _rec_name = 'name'
    
    name = fields.Char(string='Name', index=True, copy=False, default=_('New'))
    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Urgent')], 'Priority', default='0', index=True)
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Medical Facility')
    line_ids = fields.One2many(comodel_name='placement.offer.line', inverse_name='offer_id', string='Placement Lines')
    student_ids = fields.Many2many(comodel_name='res.partner', string='Students',domain=[('is_student', '=', True)], compute='_compute_offer_student_ids')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('placementing', 'Placementing'),
            ('done', 'Done'),
            ('cancel', 'Canceled'),
        ], string='Status', default='draft')
    placement_type = fields.Selection([
        ('ice', 'ICE'),
        ('tce', 'TCE'),
    ], string='Type', required=True)
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term', required=True)
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year', required=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('offer')
        return super(PlacementOffer, self).create(vals)
    
    @api.depends('line_ids')
    def _compute_offer_student_ids(self):
        for rec in self:
            rec.student_ids = rec.line_ids.mapped('student_ids')

    def action_prograss(self):
        if len(self.line_ids) == 0:
            raise ValidationError(_('you should add at least one offer'))
        empty_offers_ids = self.line_ids.filtered(lambda x: x.offers <= 0)
        if empty_offers_ids:
            offers = []
            for empty_offers_id in empty_offers_ids:
                offers += [empty_offers_id.name]
            raise ValidationError(_('%s %s should not be non-zero or less' % ('offers' if len(offers) > 1 else 'offer', offers)))
            

        self.write({
            'state': 'placementing'
        })
    def action_complete(self):
        self.write({
            'state': 'done'
        })
        
    def action_cancel(self):
        self.write({
            'state': 'cancel',
        })
        
    def action_draft(self):
        self.write({
            'state': 'draft',
        })
    # #------------------------------------------------------------------------------
    # @api.model
    # def get_view(self, view_id=None, view_type='form', **options):
    #     res = super().get_view(view_id=view_id, view_type=view_type, options=options)
    #     if view_type == 'form':
    #         doc = etree.fromstring(res['arch'])
    #         for field in self._fields:
    #                 if field != 'line_ids':
    #                     print(field)
    #                     field_xpath = "//field[@name='%s']" % field
    #                     nodes = doc.xpath(field_xpath)
    #                     for node in nodes:
    #                         modifiers = json.loads(node.get('modifiers') or '{}')

    #                         modifiers['readonly'] = [['state', '!=', 'draft']]
    #                         node.set('modifiers', json.dumps(modifiers))
    #         res['arch'] = etree.tostring(doc, encoding='unicode')
    #     return res

class PlacementOfferLine(models.Model):
    _name = 'placement.offer.line'

    name = fields.Char(string='Name')
    offer_id = fields.Many2one(comodel_name='placement.offer', string='Parent Offer')
    parent_state = fields.Selection(related='offer_id.state')
    placement_type = fields.Selection(related='offer_id.placement_type')
    placement_term = fields.Selection(related='offer_id.placement_term')
    setting = fields.Selection(string='Setting', selection=[('ip', 'IP'), ('op', 'OP')], default='op', required=True)
    offers = fields.Integer(string='Offers')
    avalible_stu_count = fields.Integer(string='Avalible Student', compute='_compute_avalible_stu_count', store=False)
    student_ids = fields.Many2many(comodel_name='res.partner', string='Students',domain=[('is_student', '=', True)])
    status = fields.Selection([
            ('Pending', 'Watting for Confirmation'),
            ('Confirmed', 'Confirmed'),
            ('not_placed', 'Not Placed'),
        ], string='Status', default='Pending')
    
    @api.depends('offers')
    def _compute_avalible_stu_count(self):
        for rec in self:
            student_count = len(rec.student_ids)
            rec.avalible_stu_count = 0 if student_count - student_count < 0 else student_count - student_count
    

    