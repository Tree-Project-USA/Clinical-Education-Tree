# -*- coding: utf-8 -*-
from lxml import etree
import json
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]
class PlacementOffer(models.Model):
    _name = 'placement.offer'
    _inherit = ['mail.thread']
    _description = 'Placement Offer'
    _rec_name = 'name'
    
    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', index=True, copy=False, default=_('New'))
    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Urgent')], 'Priority', default='0', index=True)
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Medical Facility')
    main_department_id = fields.Many2one(comodel_name='facility.department' , related='facility_id.main_department_id')
    street = fields.Char(related='main_department_id.street')
    city = fields.Char(related='geographical_id.city')
    geographical_state = fields.Char(related='geographical_id.state')
    geographical_id = fields.Many2one(comodel_name='geographical', related='main_department_id.geographical_id')
    zip_code = fields.Char(related='geographical_id.zip_code')
    line_ids = fields.One2many(comodel_name='placement.offer.line', inverse_name='offer_id', string='Placement Lines', check_company=True)
    student_ids = fields.Many2many(comodel_name='res.partner', string='Students',domain=[('is_student', '=', True)], compute='_compute_offer_student_ids')
    state = fields.Selection([
            ('offer_details_entered', 'Offer Details Entered'),
            ('offer_still_available', 'Offer Still Available'),
            ('offer_matched', 'Offer Matched'),
            ('offer_cancel', 'Offer Canceled'),
        ], string='Status', default='offer_details_entered')
    # experience_id = fields.Many2one(comodel_name='clinical.experience', string='Clinical Experience', domain="[('company_id', '=', company_id)]", required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    archive_offer_ids = fields.One2many(comodel_name='archive.offer', inverse_name='offer_id', string='Archive Offer', check_company=True)
    archive_offer_count = fields.Integer(compute='_compute_archive_offer_count', string='Archive Offer Count')
    blocked_ids = fields.Many2many(comodel_name='res.partner', string='Blocked Students')
    is_single_facility = fields.Boolean(related='facility_id.is_single_facility', store=True)
    
    
    @api.depends('archive_offer_ids')
    def _compute_archive_offer_count(self):
        for rec in self:
            rec.archive_offer_count = len(rec.archive_offer_ids)
    
    
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
        
        if self.line_ids:
            offers = []
            for counter, empty_offers_id in enumerate(self.line_ids):
                if empty_offers_id.offers <= 0:
                    offers += [f'{self.number_to_ordinal(counter+1)} line in {self.main_department_id.name if not self.is_single_facility else empty_offers_id.name}']
            if offers:
                raise ValidationError(_('%s %s should not be non-zero or less' % ('offers' if len(offers) > 1 else 'offer', offers)))
    
        archive_offer_model = self.env['archive.offer']
        for line_id in self.line_ids:
            for x in range(line_id.offers):
                archive_offer_model.create({
                    'department_id': self.main_department_id.id if self.is_single_facility else line_id.department_id.id,
                    'experience_id': line_id.experience_id.id,
                    'placement_term': line_id.placement_term,
                    'year': line_id.year,
                    'offer_id': self.id,
                    'offer_line_id': line_id.id
                })

        self.write({
            'state': 'offer_still_available'
        })
        
    def number_to_ordinal(self, number):
        if number == 1:
            return "first"
        elif number == 2:
            return "second"
        elif number == 3:
            return "third"
        else:
            return str(number) + "th"  # For numbers greater than 3, add "th" suffix

    def action_complete(self):
        self.write({
            'state': 'offer_matched'
        })
                
    def _check_linked_data(self):
        linked_data = self.archive_offer_ids.filtered(lambda line: line.is_linked)
        linked_student = self.archive_offer_ids.mapped('student_id')
        if linked_data or linked_student:
            raise ValidationError(_("You can't perform this action because the offer is already linked to students."))

    def action_cancel(self):
        self._check_linked_data()
        self.action_reset_offers()
        self.write({'state': 'offer_cancel'})

    def action_draft(self):
        self._check_linked_data()
        self.action_reset_offers()
        self.write({'state': 'offer_details_entered'})
        
    def action_reset_offers(self):
        self.archive_offer_ids.unlink()

    def action_open_archive_offer_ids(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.action_archive_offer')
        action.update({
            'view_mode': 'tree',
            'view_id': self.env.ref('clinical_decision_making.archive_offer_view_tree').id,
            'views': [(self.env.ref('clinical_decision_making.archive_offer_view_tree').id, 'tree')],
            'res_id': self.id,
            'domain': [('id', 'in', self.archive_offer_ids.ids), ('active', '=', True)],
        })
        return action
    
    @api.onchange('facility_id')
    def _onchange_facility_id(self):
        for rec in self:
            rec.archive_offer_ids = False
            rec.archive_offer_ids.unlink()
                
    @api.onchange('archive_offer_ids')
    def _onchange_archive_offer_ids(self):
        for rec in self.filtered(lambda record: record.state == 'offer_still_available'):
            lenth = len(rec.archive_offer_ids)
            linked_data = self.archive_offer_ids.filtered(lambda line: line.is_linked)
            linked_student = self.archive_offer_ids.mapped('student_id')
            if linked_data == lenth and linked_student == lenth:
                rec.write({
                    'state': 'offer_matched'
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

    #                         modifiers['readonly'] = [['state', '!=', 'offer_details_entered']]
    #                         node.set('modifiers', json.dumps(modifiers))
    #         res['arch'] = etree.tostring(doc, encoding='unicode')
    #     return res

class PlacementOfferLine(models.Model):
    _name = 'placement.offer.line'
    _description = "Offer line"

    name = fields.Char(string='Name')
    facility_id = fields.Many2one(comodel_name='medical.facility', related='offer_id.facility_id', store=True, check_company=True)
    department_id = fields.Many2one(comodel_name='facility.department' , string='Department', domain="[('id', 'in', department_ids)]", check_company=True)
    street = fields.Char(related='department_id.street')
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    geographical_id = fields.Many2one(comodel_name='geographical', related='department_id.geographical_id')
    department_ids = fields.Many2many(comodel_name='facility.department', compute="_get_facility_departments")
    archive_offer_ids = fields.One2many(comodel_name='archive.offer', inverse_name='offer_line_id', string='Archive Offer', check_company=True)
    
    
    @api.depends('facility_id')
    def _get_facility_departments(self):
        for rec in self:
            rec.department_ids = rec.facility_id.department_ids
    
    experience_id = fields.Many2one(comodel_name='clinical.experience', string='Clinical Experience', domain="[('company_id', '=', company_id)]", required=True)
    company_id = fields.Many2one('res.company', related='offer_id.company_id', store=True)
    placement_term = fields.Selection([
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ], string='Term')
    year = fields.Selection(selection=SELECTION_YEAR_RANGE, string='Year')
    offer_id = fields.Many2one(comodel_name='placement.offer', string='Parent Offer')
    parent_state = fields.Selection(related='offer_id.state')
    setting = fields.Selection(string='Setting', selection=[('ip', 'IP'), ('op', 'OP')], default='op', required=True)
    offers = fields.Integer(string='Offers')
    status = fields.Selection([
            ('Pending', 'Watting for Confirmation'),
            ('Confirmed', 'Confirmed'),
            ('not_placed', 'Not Placed'),
        ], string='Status', default='Pending')
    
