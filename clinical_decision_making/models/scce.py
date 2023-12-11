# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SCCE(models.Model):
    _name = 'scce'
    _description = 'SCCE'
    _rec_name = 'name'
    
    name = fields.Char(compute='_compute_field_name', string='Name')
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    email = fields.Char(string='Email Address')   
    facility_count = fields.Integer(compute='_compute_facility_count', string='Facility Count', store=False)
    
    def _compute_facility_count(self):
        for rec in self:
            rec.facility_count = len(self.env['medical.facility'].search([('scce_ids', 'in', self.ids)]))
    
    @api.depends('first_name', 'last_name')
    def _compute_field_name(self):
        for rec in self:
            rec.name = rec.first_name + ', ' + rec.last_name
    
    def action_open_facility(self):
        facility_ids = self.env['medical.facility'].search([('scce_ids', 'in', self.ids)])
        return {
            'name': _("Medical Facility"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'medical.facility',
            'domain': [('id', 'in', facility_ids.ids)],
            'context': {'create': False, 'edit': False, 'delete': False}
        }