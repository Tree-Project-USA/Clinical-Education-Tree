# -*- coding: utf-8 -*-
##################################################################################
#                                                                                #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: www.ekikacorporation.com). #
# See LICENSE file for full copyright and licensing details.                     #
#                                                                                #
##################################################################################

from odoo import models, fields

class OAuth2Token(models.Model):
    _name = 'oauth2.token'
    _description = 'OAuth2 Token'

    name = fields.Char('Name')
    client_id = fields.Many2one('oauth2.client','Client')
    user_id = fields.Many2one('res.users','User')
    scopes = fields.Text('Scopes')
    access_token = fields.Text('Access Token') # access_token should be unique
    refresh_token = fields.Text('Refresh Token') # refresh_token should be unique
    expire_time = fields.Datetime('Expiration Time')
