# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class FacilityDepartment(models.Model):
    _name = 'facility.department'
    _description = _('Clinical Site Location')
    _rec_name = 'complete_name'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Clinical Site', ondelete='cascade')
    facility_scce_ids = fields.Many2many(comodel_name='scce.facility', string='Clinical Site SCCE', compute='_compute_facility_scce')
    scce_ids = fields.Many2many(comodel_name='scce.facility', string='SCCE', domain="[('id', 'in', facility_scce_ids)]")
    setting_ids = fields.Many2many(comodel_name='preferred.setting', string='Setting')
    street = fields.Char(string='Street')
    geographical_id = fields.Many2one(comodel_name='geographical', string='Zip Code')
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    zip = fields.Char(related='geographical_id.zip_code')
    latitude = fields.Char(related='geographical_id.latitude', store=True)
    longitude = fields.Char(related='geographical_id.longitude', store=True)
    is_main_department = fields.Boolean(string='Main Department', default=False, copy=False)
    active_state = fields.Selection(
        string=_('Contract Status'),
        selection=[
            ('active', 'Active'),
            ('not_active', 'Not Active'),
        ],
        compute='_compute_active_state',
    )
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)

    @api.depends('active')
    def _compute_active_state(self):
        for record in self:
            record.active_state = 'active' if record.active else 'not_active'
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
        action = self.env.ref('cdm_base.student_action').sudo().read()[0]
        action['domain'] = [('id', 'in', student_ids.ids)]
        action['context'] = {'create': False, 'delete': False, 'active_test': False}
        return action
    
    def action_view_facility_department(self):
        self.ensure_one()
        action = self.env.ref('cdm_base.action_facility_department').sudo().read()[0]
        action['view_mode'] = 'form'
        action['res_id'] = self.id
        action['views'] = [(False, "form")]
        action['view_id'] = self.env.ref('cdm_base.view_facility_department_form').id
        action['context'] = {'default_facility_id': self.facility_id.id}
        return action

    def archive_department(self):
        self.write({
            'active': False
        })

    def unarchive_department(self):
        self.write({
            'active': True
        })
