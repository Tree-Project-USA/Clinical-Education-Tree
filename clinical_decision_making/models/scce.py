# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re



class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_scce = fields.Boolean(string='Is SCCE', default=False)
    facility_count = fields.Integer(compute='_compute_facility_count', string='Facility Count', store=False)
    
    def _compute_facility_count(self):
        for rec in self:
            rec.facility_count = len(self.env['medical.facility'].search([('scce_ids', 'in', self.ids)]))
    
    
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
    
class SCCE(models.Model):
    _name = 'scce'
    _description = 'SCCE'
    _rec_name = 'name'
    
    scceid = fields.Char(string='SCCE ID', copy=False)
    name = fields.Char(compute='_compute_field_name', string='Name')
    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    email = fields.Char(string='Email Address')
    phone = fields.Char(string='Phone Number')
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
    
    def _check_unique_scceid(self, scceid):
        if scceid:
            pattern = r'^\d+$'
            if not re.match(pattern, scceid):
                raise ValidationError(_('The SCCE ID Must Contain Numbers Only'))
            scce_ids = self.env['scce'].search_count(
                    [
                    ("scceid", "in", [scceid]),
                    ])
            if scce_ids > 1:
                raise ValidationError(_(f'The SCCE ID : {scceid} Already Exists'))

    @api.model
    def _get_scceid_sequence(self):
        code = self.env['ir.sequence'].next_by_code('scce_sequence')
        scce_ids = self.env['scce'].search_count(
            [
            ("scceid", "=", code),
            ])
        if not scce_ids:
            return code
        else:
            return self._get_scceid_sequence()

    @api.model
    def create(self, vals):
        if not vals['scceid']:
            vals['scceid'] = self._get_scceid_sequence()
        else:
            self._check_unique_scceid(vals['scceid'])
        return super(SCCE, self.with_context(pass_validation=True)).create(vals)