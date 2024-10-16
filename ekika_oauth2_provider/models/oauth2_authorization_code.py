# -*- coding: utf-8 -*-
##################################################################################
#                                                                                #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: www.ekikacorporation.com). #
# See LICENSE file for full copyright and licensing details.                     #
#                                                                                #
##################################################################################

from odoo import models, fields

class OAuth2AuthorizationCode(models.Model):
    _name = 'oauth2.authorization.code'
    _description = 'OAuth2 Authorization Code'

    name = fields.Char('Name')
    client = fields.Many2one('oauth2.client',string='Client')
    client_id = fields.Text('Client-Id')
    user_id = fields.Many2one('res.users', string='User')
    scopes = fields.Text('Scopes')
    auth_code = fields.Text('Authorization Code') # auth_code should be unique
    redirect_uri = fields.Text('Redirect Uri')
    expire_time = fields.Datetime('Expiration Time')
