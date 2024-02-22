# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class FacilityDepartment(models.Model):
    _name = 'facility.department'
    _description = _('Clinical Site Department')
    _rec_name = 'complete_name'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Clinical Site', ondelete='cascade')
    facility_scce_ids = fields.Many2many(comodel_name='scce.facility', string='Clinical Site SCCE', compute='_compute_facility_scce')
    scce_ids = fields.Many2many(comodel_name='scce.facility', string='SCCE', domain="[('id', 'in', facility_scce_ids)]")
    setting_ids = fields.Many2many(comodel_name='preferred.setting', string='Setting')
    street = fields.Char(string='Street')
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    geographical_id = fields.Many2one(comodel_name='geographical', string='Zip Code')
    is_main_department = fields.Boolean(string='Main Department', default=False, copy=False)
    student_count = fields.Integer(compute='_compute_count', string='Student Count')
    archive_offer_count = fields.Integer(compute='_compute_count')
    active_state = fields.Selection(
        string=_('Contract Status'),
        selection=[
            ('active', 'Active'),
            ('not_active', 'Not Active'),
        ],
        compute='_compute_active_state',
    )
    archive_ids = fields.One2many(comodel_name='archive', inverse_name='department_id', string='Placement History')
    archive_count = fields.Integer(compute='_compute_count', string='Placement History Count')
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)
    archive_offer_ids = fields.One2many(comodel_name='archive.offer', inverse_name='department_id', string='Archive Offer')

    def _compute_count(self):
        for rec in self:
            rec.student_count = len(self.env['archive'].with_context(active_test=False).search([('department_id', '=', rec.id), ('placement_status', 'in', ['completed', 'confirmed'])]).mapped('student_id'))
            rec.archive_offer_count = len(self.env['archive.offer'].search([('department_id', '=', rec.id)]))
            rec.archive_count = len(rec.archive_ids)
            
    @api.depends('active')
    def _compute_active_state(self):
        for record in self:
            record.active_state = 'active' if record.active else 'not_active'
    
    @api.depends('facility_id', 'facility_id.scce_ids')
    def _compute_facility_scce(self):
        for rec in self:
            rec.facility_scce_ids = rec.facility_id.scce_ids

    @api.depends('name', 'facility_id.name')
    def _compute_complete_name(self):
        for department in self:
            if not department.is_main_department:
                department.complete_name = '%s / %s' % (department.facility_id.name, department.name)
            else:
                department.complete_name = department.name
    
    # CRUD Operations
    #------------------------------------------------------------------------------   
    def unlink(self):
        if self.env.context.get('unlink_main_department', False):
            return super(FacilityDepartment, self).unlink()
        else:
            return super(FacilityDepartment, self.filtered(lambda x: not x.is_main_department)).unlink()
         
    # Smart Button Action Methods
    #------------------------------------------------------------------------------
    def action_view_students(self):
        student_ids = self.env['archive'].search([('department_id', '=', self.id), ('placement_status', 'in', ['completed', 'confirmed'])]).mapped('student_id')
        action = self.env.ref('clinical_decision_making.student_action').sudo().read()[0]
        action['domain'] = [('id', 'in', student_ids.ids)]
        action['context'] = {'create': False, 'delete': False, 'active_test': False}
        return action
    
    def action_open_department_archive_offer(self):
        archive_offer_ids = self.env['archive.offer'].search([('department_id', '=', self.id)])
        action = self.env['ir.actions.actions']._for_xml_id('clinical_decision_making.action_archive_offer')
        action.update({
            'view_mode': 'tree',
            'view_id': self.env.ref('clinical_decision_making.archive_offer_view_tree').id,
            'views': [(self.env.ref('clinical_decision_making.archive_offer_view_tree').id, 'tree')],
            'domain': [('id', 'in', archive_offer_ids.ids), ('active', '=', True)],
        })
        return action
    
    def action_view_facility_department(self):
        self.ensure_one()
        action = self.env.ref('clinical_decision_making.action_facility_department').sudo().read()[0]
        action['view_mode'] = 'form'
        action['res_id'] = self.id
        action['views'] = [(False, "form")]
        action['view_id'] = self.env.ref('clinical_decision_making.view_facility_department_form').id
        action['context'] = {'default_facility_id': self.facility_id.id}
        return action
    
    def action_view_placement_history(self):
        self.ensure_one()
        action = self.env.ref('clinical_decision_making.archive_action').sudo().read()[0]
        action['view_mode'] = 'tree'
        action['views'] = [(self.env.ref('clinical_decision_making.archive_view_tree').id, 'tree')]
        action['view_id'] = self.env.ref('clinical_decision_making.archive_view_tree').id
        action['context'] = {'default_department_id': self.id}
        action['domain'] = [('id', 'in', self.archive_ids.ids), ('active', '=', True)]
        return action

       
    # Archive Methods
    #------------------------------------------------------------------------------   
    
    def archive_department(self):
        self.write({
            'active': False
        })

    def archive_department_and_offers(self):
        self.env['archive.offer'].search([('department_id', 'in', self.ids), '|', ('is_linked', '=', False), ('student_id', '=', False)]).write({
            'active': False
        })
        self.write({
            'active': False
        })

    def archive_department_and_unlink_offers(self):
        self.env['archive.offer'].search([('department_id', 'in', self.ids), '|', (
            'is_linked', '=', False), ('student_id', '=', False)]).unlink()
        self.write({
            'active': False
        })

    def unarchive_department(self):
        self.write({
            'active': True
        })

    def unarchive_department_and_offers(self):
        self.write({
            'active': True
        })
        self.env['archive.offer'].search([('department_id', 'in', self.ids), ('active', '=', False)]).write({
            'active': True
        })

    def unarchive_department_and_unlink_offers(self):
        self.write({
            'active': True
        })
        self.env['archive.offer'].search([('department_id', 'in', self.ids), '|', (
            'is_linked', '=', False), ('student_id', '=', False)]).unlink()
