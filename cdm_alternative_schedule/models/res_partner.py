# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    alternative_schedule_ids = fields.One2many('alternative.schedule', 'student_id', string='Alternative Schedule')
    alternative_schedule_count = fields.Integer(compute='_compute_alternative_schedule_count', string='Alternative Schedule Count')

    @api.depends('alternative_schedule_ids')
    def _compute_alternative_schedule_count(self):
        for rec in self:
            rec.alternative_schedule_count = len(rec.alternative_schedule_ids)
    
    def alternative_schedule_term_action(self):
        self.ensure_one()
        # This assumes the action XML ID will be updated if needed or kept as is
        action = self.env['ir.actions.actions']._for_xml_id('cdm_alternative_schedule.action_alternative_schedule')
        action.update({
            'name': 'Alternative Schedule of %s' % self.name,
            'context': {'default_student_id': self.id},
            'view_mode': 'form',
            'view_id': self.env.ref('cdm_alternative_schedule.alternative_schedule_form_view_wizard').id,
            'views': [(self.env.ref('cdm_alternative_schedule.alternative_schedule_form_view_wizard').id, 'form')],
            'target': 'new'
        })
        return action

    def action_view_alternative_schedule(self):
        action = self.env.ref('cdm_alternative_schedule.action_alternative_schedule').sudo().read()[0]
        action['domain'] = [('id', 'in', self.alternative_schedule_ids.ids)]
        action['context'] = {'create': False, 'delete': False, 'edit': False}
        return action
