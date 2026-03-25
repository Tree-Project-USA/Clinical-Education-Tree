# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    hardship_ids = fields.One2many('hardship.request', 'student_id', string='Hardship')
    hardship_count = fields.Integer(compute='_compute_hardship_count', string='HardShip Count')
    is_with_hardship = fields.Boolean(string='is_with_hardship', compute='_compute_is_with_hardship', store=True)
    deny_show_student = fields.Boolean(string='Deny Show Student', default=False)
    can_apply_hardship = fields.Boolean(string='Can Apply Hardship', default=True)

    @api.depends('hardship_ids')
    def _compute_hardship_count(self):
        for rec in self:
            rec.hardship_count = len(rec.hardship_ids)

    @api.depends('hardship_ids', 'hardship_ids.state')
    def _compute_is_with_hardship(self):
        for rec in self:
            rec.is_with_hardship = any(x.state == 'approved' for x in rec.hardship_ids)
    
    def action_open_hardship(self):
        return {
            'name': _("Student Hardship"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'hardship.request',
            'domain': [('id', 'in', self.hardship_ids.ids)],
            'context': {'default_student_id': self.id, 'delete': False}
        }
