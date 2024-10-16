# -*- coding: utf-8 -*-
##################################################################################
#                                                                                #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: www.ekikacorporation.com). #
# See LICENSE file for full copyright and licensing details.                     #
#                                                                                #
##################################################################################

from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    # ToDo: For next version, These are clients which are authorized by user
    oauth_client_ids = fields.Many2many('oauth2.client', string='Authorized clients')

    def is_authorized_oauth_client(self, client_id):
        self.ensure_one()
        authorized_client_ids = [v['client_id'] for v in self.oauth_client_ids]
        return client_id in authorized_client_ids
