# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Archive(models.Model):
    _inherit = 'archive'

    def write(self, vals):
        res = super(Archive, self).write(vals)
        if 'placement_status' in vals:
            for rec in self:
                if rec.placement_status == 'confirmed':
                    ptse_1_survey = rec.experience_id.ptse_1_survey    
                    ptse_2_survey = rec.experience_id.ptse_2_survey
                    user_input_1 = ptse_1_survey.mapped('user_input_ids').search([
                        ('partner_id', '=', rec.student_id.id),
                        ('state', '=', 'done'),
                        ('survey_id', '=', ptse_1_survey.id)
                    ])
                    user_input_2 = ptse_2_survey.mapped('user_input_ids').search([
                        ('partner_id', '=', rec.student_id.id),
                        ('state', '=', 'done'),
                        ('survey_id', '=', ptse_2_survey.id)
                    ])
                    self.env["post.plcement.management"].sudo().create({
                        'archive_id': rec.id,
                        'student_id': rec.student_id.id,
                        'facility_id': rec.department_id.facility_id.id,
                        'experience_id': rec.experience_id.id,
                        'year': rec.year if rec.year else False,
                        'placement_term': rec.placement_term if rec.placement_term else False,
                        'ptse_1': user_input_1.id if user_input_1 else False,
                        'ptse_2': user_input_2.id if user_input_2 else False,
                    })
        return res
