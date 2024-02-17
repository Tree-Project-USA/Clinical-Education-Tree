# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_open_user_company(self):
    
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('base.action_res_company_form')
        action['context'] = {'create': False, 'delete': False}
        action.update({
            'view_mode': 'form',
            'view_id': self.env.ref('clinical_decision_making.view_res_company_form_inherit').id,
            'views': [(self.env.ref('clinical_decision_making.view_res_company_form_inherit').id, 'form')],
            'res_id': self.company_id.id,
        })
        return action