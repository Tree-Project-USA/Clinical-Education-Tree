# -*- encoding: utf-8 -*-

from odoo import api, fields, models


class PreferredSetting(models.Model):
    _name = 'preferred.setting'
    _description = 'Preferred Setting'


    name = fields.Char()
    type_setting = fields.Selection(
        string="Type",
        selection=[
                ('ip', 'IP'),
                ('op', 'OP'),
        ],
    )
