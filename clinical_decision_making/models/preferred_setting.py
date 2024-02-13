# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class PreferredSetting(models.Model):
    _name = 'preferred.setting'
    _description = 'Preferred Setting'


    name = fields.Char()
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)
    type_setting = fields.Selection(
        string="Type",
        selection=[
                ('ip', 'IP'),
                ('op', 'OP'),
        ],
    )
