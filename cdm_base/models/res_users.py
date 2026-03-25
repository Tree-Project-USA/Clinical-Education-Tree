# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_open_user_company(self):
    
        self.ensure_one()
        action = self.env.ref('base.action_res_company_form').sudo().read()[0]
        action['context'] = {'create': False, 'delete': False}
        action.update({
            'view_mode': 'form',
            'view_id': self.env.ref('cdm_base.view_res_company_form_inherit').id,
            'views': [(self.env.ref('cdm_base.view_res_company_form_inherit').id, 'form')],
            'res_id': self.company_id.id,
        })
        return action