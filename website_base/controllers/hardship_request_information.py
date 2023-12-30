import base64
import json
from odoo import http
from odoo.http import request


class HardshipInformation(http.Controller):

    @http.route("/hardship/request/inforamtion", type="http", website=True, auth="user")
    def hardship_request_information(self):
        values = {}
        partner_id = request.env.user.partner_id
        hardship_id = request.env["hardship.request"].sudo().search([
            ('student_id', '=', partner_id.id),
            ], limit=1, order="id desc")
        values["hardship_id"] = hardship_id
        return request.render("website_base.hardship_information_template", values)
    