# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import content_disposition, request
from werkzeug.urls import url_decode, url_encode, url_parse
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import TableCompute, WebsiteSale
from odoo.addons.website.controllers.main import Website
from werkzeug.exceptions import NotFound

import logging

_logger = logging.getLogger(__name__)


class TADWebsite(Website):
    @http.route('/', type='http', auth='public', website=True, sitemap=True)
    def index(self, **kw):
        response = super(TADWebsite, self).index(**kw)
        if request.website.theme_id.sudo().name == 'them_cpdm':
            return request.render('them_cpdm.home', response.qcontext)

        return response

