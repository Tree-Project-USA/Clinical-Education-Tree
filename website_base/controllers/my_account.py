import base64
import requests
from datetime import datetime
import json
from odoo import _, http
from odoo.http import request, route
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortals(CustomerPortal):
    
    @route([])
    def home(self):
        values = {}
        res_partner_id = request.env.user.partner_id
        if not res_partner_id.is_scce:
            hardship_id = request.env["hardship.request"].sudo().search([
                ('student_id', '=', res_partner_id.id)
            ], limit=1, order="id desc")
            values["partner"] = res_partner_id
            values["hardship"] = hardship_id
            return request.render("website_base.user_profile_templates", values)
        else:
            scce_facility_ids = request.env["scce.facility"].sudo().search([
                ('scce_id', '=', res_partner_id.id)]).mapped("facility_id")
            values["partner"] = res_partner_id
            values["scce_facility_ids"] = scce_facility_ids
            return request.render("website_base.scce_profile_template", values)
  