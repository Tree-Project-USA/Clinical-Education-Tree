# -*- coding: utf-8 -*-
##################################################################################
#                                                                                #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: www.ekikacorporation.com). #
# See LICENSE file for full copyright and licensing details.                     #
#                                                                                #
##################################################################################

from oauthlib.common import Request
from oauthlib.oauth2 import RequestValidator
from oauthlib.oauth2.rfc6749.clients import Client
import datetime
from odoo.http import request as odooReq

class EasyOAuth2Validator(RequestValidator):

    def validate_client_id(self, client_id, request, *args, **kwargs):
        try:
            # ToDo: we can also check if client is active or not by adding active field to model
            client = odooReq.env['oauth2.client'].sudo().search([('client_id','=',client_id)])
            if client:
                request.client = client
                return True
            else:
                return False
        except Exception as exc:
            raise exc

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs) -> bool:
        try:
            if request.client:
                return redirect_uri in request.client.redirect_uris.split(' ')
            else:
                client = odooReq.env['oauth2.client'].sudo().search([
                    ('client_id','=',client_id)])
                request.client = client
                if client and redirect_uri in request.client.redirect_uris.split(' '):
                    return True
                else:
                    return False
        except Exception as exc:
            raise exc

    def get_default_redirect_uri(self, client_id: str, request: Request, *args, **kwargs) -> str:
        try:
            if request.client:
                return request.client.default_redirect_uri if request.client.default_redirect_uri else None
            else:
                client = odooReq.env['oauth2.client'].sudo().search([
                    ('client_id','=',client_id)])
                request.client = client
                if request.client:
                    return request.client.default_redirect_uri if request.client.default_redirect_uri else None

        except Exception as exc:
            raise exc

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs) -> bool:
        return set(scopes).issubset(set(client.scopes.split(' ')))

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        if request.client:
            return request.client.default_scope.split(' ')
        else:
            client = odooReq.env['oauth2.client'].sudo().search([
                ('client_id','=',client_id)])
            request.client = client
            if request.client:
                return request.client.default_scope.split(' ')

    def validate_response_type(self, client_id, response_type, client, request,
                               *args, **kwargs) -> bool:
        # ToDo: Currently, we only support authorization_code grant
        if request.client:
            if request.client.grant_type == 'authorization_code':
                return response_type == 'code'
            elif request.client.grant_type == 'implicit_grant':
                return response_type == 'token'
        else:
            client = odooReq.env['oauth2.client'].sudo().search([
                    ('client_id','=',client_id)])
            request.client = client
            if request.client.grant_type == 'authorization_code':
                return response_type == 'code'
            elif request.client.grant_type == 'implicit_grant':
                return response_type == 'token'

    def save_authorization_code(self, client_id: str, code, request: Request,
                                *args, **kwargs) -> None:
        try:
            odooReq.env['oauth2.authorization.code'].sudo().create({
                'client': request.client.id,
                'client_id': client_id,
                'scopes': ' '.join(request.scopes),
                'redirect_uri': request.redirect_uri,
                'auth_code': code['code'],
                'user_id': request.user,
                'expire_time':  datetime.datetime.utcnow() + datetime.timedelta(minutes=10) # ToDo. Expiration 10 minutes
            })
        except Exception as exc:
            raise exc

    def client_authentication_required(self, request: Request, *args, **kwargs) -> bool:
        # ToDo: currently, client authentication required
        return True

    def authenticate_client(self, request: Request, *args, **kwargs) -> bool:
        # ToDo: We can also use client credentials for authentication purpose
        client = odooReq.env['oauth2.client'].sudo().search([('client_id','=', request.client_id)])
        if client:
            request.client = client
            # ToDo: Here, we have assign user as client-user in client_credentials grant
            if request.grant_type == 'client_credentials':
                request.user = request.client.user_id.id
            return True
        else:
            return False

    def authenticate_client_id(self, client_id: str, request: Request, *args, **kwargs) -> bool:
        client = odooReq.env['oauth2.client'].sudo().search([('client_id','=', request.client_id)])
        return True if client else False

    def validate_code(self, client_id: str, code: str, client: Client,
                      request: Request, *args, **kwargs) -> bool:
        auth_code = odooReq.env['oauth2.authorization.code'].sudo().search([
            ('auth_code','=',code),('client_id','=',client_id),('client','=',client.id)
            ])
        if auth_code:
            request.user = auth_code.user_id.id
            request.scopes = auth_code.scopes.split(' ')
            return True if auth_code.expire_time > datetime.datetime.utcnow() else False
        else:
            return False

    def confirm_redirect_uri(self, client_id: str, code: str, redirect_uri: str, client: Client,
                             request: Request, *args, **kwargs) -> bool:
        auth_code = odooReq.env['oauth2.authorization.code'].sudo().search([
            ('auth_code','=',code),('client_id','=',client_id),('client','=',client.id)
            ]) 
        return True if redirect_uri == auth_code.redirect_uri else False

    def validate_grant_type(self, client_id: str, grant_type: str, client: Client,
                            request: Request, *args, **kwargs) -> bool:
        """
        for authorization_code_grant, grant_type can be authorization_code or refresh_token
        """
        return True if grant_type == client.grant_type or grant_type == 'refresh_token' else False

    def save_bearer_token(self, token: dict, request: Request, *args, **kwargs) -> str:
        """
        ToDo: 'scope': 'string of space separated authorized scopes',
                as described in docstring of abstract method
        """
        odooReq.env['oauth2.token'].sudo().create({
            'access_token': token.get('access_token'),
            'refresh_token': token.get('refresh_token'),
            'expire_time': datetime.datetime.utcnow() + datetime.timedelta(seconds=token['expires_in']),
            'scopes': ' '.join(request.scopes),
            'client_id': request.client.id,
            'user_id': request.user,
        })

    def invalidate_authorization_code(self, client_id: str, code: str, request: Request,
                                      *args, **kwargs) -> None:
        auth_code = odooReq.env['oauth2.authorization.code'].sudo().search([
            ('auth_code','=',code),('client_id','=',client_id)
            ])
        auth_code.unlink()

    def validate_bearer_token(self, token: str, scopes, request: Request) -> bool:
        """
        ToDo: access according to scopes
        """
        access_token = odooReq.env['oauth2.token'].sudo().search([('access_token', '=', token)])
        if access_token:
            if access_token.expire_time > datetime.datetime.utcnow():
                return True
            else:
                return False
        else:
            return False

    def get_original_scopes(self, refresh_token: str, request: Request, *args, **kwargs):
        """
        ToDo: token record should have scopes
        """
        token = odooReq.env['oauth2.token'].sudo().search([('refresh_token', '=', refresh_token)])
        if token:
            return token.scopes
        else:
            return ''

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        token = odooReq.env['oauth2.token'].sudo().search([('refresh_token', '=', refresh_token),
                                                        ('client_id', '=', client.id)])
        if token:
            if refresh_token == token.refresh_token:
                request.user = token.user_id.id
                return True
            else:
                return False
        else:
            return False

    def validate_user(self, username: str, password: str, client: Client,
                      request: Request, *args, **kwargs) -> bool:
        try:
            user_id = odooReq.session.authenticate(odooReq.db, username, password)
        except:
            return False
        else:
            if user_id:
                request.user = user_id
                return True
            else:
                return False

    def revoke_token(self, token: str, token_type_hint: str, request: Request, *args, **kwargs) -> None:
        # ToDo: Curretly, We are searching for both access_token or refresh_token record
        refresh_token = odooReq.env['oauth2.token'].sudo().search(['|', ('access_token','=',token),
                                                               ('refresh_token','=',token)])
        # Delete refresh-token related clients and user records
        token_rec = odooReq.env['oauth2.token'].sudo()\
                    .search([('client_id','=', refresh_token.client_id.id),
                            ('user_id','=', refresh_token.user_id.id)])
        if token_rec:
            token_rec.unlink()
