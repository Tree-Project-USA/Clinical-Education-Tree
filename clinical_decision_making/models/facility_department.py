# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class FacilityDepartment(models.Model):
    _name = 'facility.department'
    _description = _('Facility Department')
    _rec_name = 'complete_name'

    name = fields.Char(string='Name', required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Facility', ondelete='cascade')
    facility_scce_ids = fields.Many2many(comodel_name='scce.facility', string='Facility SCCE', compute='_compute_facility_scce')
    scce_ids = fields.Many2many(comodel_name='scce.facility', string='SCCE', domain="[('id', 'in', facility_scce_ids)]")
    setting_ids = fields.Many2many(comodel_name='preferred.setting', string='Setting')
    street = fields.Char(string='Street')
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    geographical_id = fields.Many2one(comodel_name='geographical', string='Zip Code')
    
    is_main_department = fields.Boolean(string='Main Department', default=False, copy=False)
    
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
         
    
    # View Department Action Methods
    #------------------------------------------------------------------------------   
    def action_view_facility_department(self):
        self.ensure_one()
        action = self.env.ref('clinical_decision_making.action_facility_department').read()[0]
        action['view_mode'] = 'form'
        action['res_id'] = self.id
        action['views'] = [(False, "form")]
        action['view_id'] = self.env.ref('clinical_decision_making.view_facility_department_form').id
        action['context'] = {'default_facility_id': self.facility_id.id}
        return action
