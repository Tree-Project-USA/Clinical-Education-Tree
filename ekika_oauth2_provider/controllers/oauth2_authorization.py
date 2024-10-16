# -*- coding: utf-8 -*-
##################################################################################
#                                                                                #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: www.ekikacorporation.com). #
# See LICENSE file for full copyright and licensing details.                     #
#                                                                                #
##################################################################################

from odoo import http
from odoo.http import request, Response
from odoo.exceptions import AccessDenied
import json
from ..oauth2.server import oauth2_provider_server
from odoo.addons.ekika_utils.tools.helpers import extract_params

class OAuth2AuthorizationController(http.Controller):

    def __init__(self):
        super(OAuth2AuthorizationController, self).__init__()
        self.oauth2_endpoint = oauth2_provider_server

    @http.route('/oauth2/authorize', methods=['GET'], type='http', auth='user')
    def oauth2_authorization_code_get(self, **kwargs):
        http_method, body, uri, headers = extract_params(request)
        scopes, credentials = self.oauth2_endpoint.validate_authorization_request(
                uri, http_method, body, headers)

        client_id = credentials.get('client_id')
        client_app_name = request.env['oauth2.client'].sudo()\
                            .search([('client_id','=',client_id)]).app_name
        render_values = {
            'redirect_uri': credentials.get('redirect_uri'),
            'client_id': client_id,
            'client_app_name': client_app_name,
            'state': credentials.get('state'),
            'response_type': credentials.get('response_type'),
            'scopes': " ".join(scopes),
        }
        # To check if user logged-in
        if request.uid:
            render_values['user_id'] = request.uid
            return request.render('ekika_oauth2_provider.oauth2_authorize_form', render_values)
            # ToDo: Add functionality if user previously authorized this client,
            # then we don't have to display auhtorize form 
            if request.user.is_authorized_oauth_client(credentials.get('client_id')):
                pass
            else:
                pass

    @http.route('/oauth2/authorize', methods=['POST'], type='http', auth='user',
                save_session=False, csrf=False)
    def oauth2_authorization_code_post(self, **kwargs):
        http_method, body, uri, headers = extract_params(request)
        scopes = request.httprequest.form.get('scopes').split(' ')
        # client_id = request.params.get('client_id')
        # response_type = request.params.get('response_type')
        # redirect_uri = request.params.get('redirect_uri')
        # state = request.params.get('state')

        # ToDo: should we use "request.uid" or request parameters to get user-id?
        #       Currently we get from request parameter 
        user_id = request.params.get('user_id')
        credentials = {'user': user_id}
        try:
            headers, body, status = self.oauth2_endpoint.create_authorization_response(
            uri, http_method, body, headers, scopes, credentials)
            return Response(body, headers=headers, status=status)
        except Exception as e:
            raise e

    @http.route('/oauth2/token', methods=['POST'], type='http', auth='none',
                save_session=False, csrf=False)
    def oauth2_token_post(self, **kwargs):
        http_method, body, uri, headers = extract_params(request)
        headers, body, status = self.oauth2_endpoint.create_token_response(
                uri, http_method, body, headers, credentials={})
        res =  Response(response=body, headers=headers, status=status)
        return res

    @http.route('/oauth2/revoke', methods=['POST'], type='http', auth='none',
                save_session=False, csrf=False)
    def oauth2_token_revoke_post(self, **kwargs):
        http_method, body, uri, headers = extract_params(request)
        headers, body, status = self.oauth2_endpoint.create_revocation_response(uri,
                headers=headers, body=body, http_method=http_method)
        res =  Response(response=body, headers=headers, status=status)
        return res

    @http.route('/oauth2/userinfo', methods=['GET'], type='http', auth='none',
                save_session=False, csrf=False)
    def oauth2_user_info(self, **kwargs):
        """
        This controller is used to get basic user information
        """
        access_token = kwargs.get('access_token')
        user_rec = request.env['oauth2.token'].sudo()\
                        .search([('access_token','=',access_token)]).user_id
        valid_token = self.oauth2_endpoint.request_validator\
                            .validate_bearer_token(access_token, None, None)
        if user_rec and valid_token:
            user_info = {
                'user_id': user_rec.id,
                'email': user_rec.email,
                'name': user_rec.name,
            }
        else:
            # ToDo: Error Info
            user_info = {
                'error': 'Error!'
            }
        return Response(json.dumps(user_info), status=200)
