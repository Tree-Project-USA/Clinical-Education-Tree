# -*- coding: utf-8 -*-
##################################################################################
#                                                                                #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: www.ekikacorporation.com). #
# See LICENSE file for full copyright and licensing details.                     #
#                                                                                #
##################################################################################

from oauthlib.oauth2 import Server
from .validators import EasyOAuth2Validator

oauth2_validator = EasyOAuth2Validator()

# ToDo Currenlty we provide token_expire_in value in second,
# we can also provide token_expire_in parameter value as callable function,
# where this callable function accept 'request' parameter of oauth Lib.
# this callable function is called from "create_token() method of BearerToken class"
oauth2_provider_server = Server(oauth2_validator, token_expires_in=86400)
