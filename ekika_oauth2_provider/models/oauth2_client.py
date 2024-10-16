# -*- coding: utf-8 -*-
##################################################################################
#                                                                                #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: www.ekikacorporation.com). #
# See LICENSE file for full copyright and licensing details.                     #
#                                                                                #
##################################################################################

from odoo import models, fields, api
import secrets, string
from urllib.parse import urlparse

class OAuth2Client(models.Model):
    """
    This model is for client registration
    """
    _name = 'oauth2.client'
    _description = 'OAuth2 Client'

    name = fields.Char('Name', compute='_compute_name', store=True)
    app_name = fields.Char('App Name', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    client_id = fields.Text('Client Id', readonly=True)
    client_secret = fields.Text('Client Secret', readonly=True)
    # Currently, we have to store scope as string of space separated
    scopes = fields.Text(string='Scopes', required=True,
                        help="Provide string of space separated scopes")
    # You might also want to mark a certain URI as default in case the
    # client does not specify any in the authorization
    default_scope = fields.Text(string='Default Scope', required=True)
    # Currently, we have to store redirect_uris as string of space separated
    redirect_uris = fields.Text(string='Redirect URIs', required=True,
                                help="Provide string of space separated redirect uris")
    default_redirect_uri = fields.Text('Default Redirect URI', required=True)
    grant_type = fields.Selection(string='Grant Type', 
                                  selection=[('authorization_code', 'Authorization Code Grant'),
                                            ('implicit_grant', 'Implicit Grant'),
                                            ('password', 'Resource Owner Password Credentials Grant'),
                                            ('client_credentials', 'Client Credentials Grant')],
                                  required=True)

    @api.depends('app_name', 'grant_type')
    def _compute_name(self):
        for rec in self:
            rec.name = (f'{rec.app_name} '
                        f'({dict(rec._fields["grant_type"].selection).get(rec.grant_type)})')

    @api.constrains('client_id')
    def _check_client_id_field(self):
        for record in self:
            duplicate_records = self.search([('client_id', '=', record.client_id)])
            if len(duplicate_records) > 1:
                raise models.ValidationError('client_id field must be unique!')

    @api.constrains('client_secret')
    def _check_client_secret_field(self):
        for record in self:
            duplicate_records = self.search([('client_secret', '=', record.client_secret)])
            if len(duplicate_records) > 1:
                raise models.ValidationError('client_secret field must be unique!')

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults.setdefault('client_id', self.generate_client_id())
        defaults.setdefault('client_secret', self.generate_client_secret())
        return defaults
    
    def generate_client_id(self, length=30):
        alphabet = string.ascii_letters + string.digits
        random_string = ''.join(secrets.choice(alphabet) for _ in range(length))
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        parsed_url = urlparse(url)
        random_client_id = f'{random_string}.{parsed_url.netloc}'
        return random_client_id

    def generate_client_secret(self):
        return secrets.token_hex(64)
