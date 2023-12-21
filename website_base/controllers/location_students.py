import requests
import json
from odoo import _, http
from odoo.http import request, route
from odoo.exceptions import ValidationError


class Location(http.Controller):
    
    @http.route("/add/location", type="http", website=True, auth="user", Methods=["POST"])
    def add_location(self, **kw):
        res_partner_id = request.env.user.partner_id
        if request.httprequest.method == "GET":
            values = {}
            hardship_id = request.env["hardship.request"].sudo().search([
                ('student_id', '=', res_partner_id.id),
                ('state', '=', 'update')
            ])
            values["partner"] = res_partner_id
            values["hardship"] = hardship_id
            
            if res_partner_id.can_apply_hardship:
                can_apply_hardship = 3
            else:
                can_apply_hardship = 5
            values.update({
                'rw': can_apply_hardship
            })
            return request.render("website_base.locations_students_template", values)
        elif request.httprequest.method == "POST":
            zip_code_list = [int(i) for i in kw.get('list_zip_code').split(",") if i != ','] if kw.get('list_zip_code', False) else []
            values = {
                "geographical_ids": zip_code_list,
                "is_reach_maximum_zip_code": True,
            }
            try:
                request_dummy = request.env["res.partner"].sudo().new(values)  
                request_dummy._check_geographical_ids()
                res_partner_id.sudo().write(values)
                return request.redirect("/my/home")
            except ValidationError as msg:
                if res_partner_id.can_apply_hardship:
                    can_apply_hardship = 3
                else:
                    can_apply_hardship = 5
                values.update({
                    'rw': can_apply_hardship
                })
                error = str(msg.args[0])
                if error:
                    values["error"] = error
                    return request.render("website_base.locations_students_template", values)
    
    @http.route(
        ["/show/locations"], type="json", auth="user", website=True, csrf=False
    )
    def show_locations(self, zip_code=None, **post):
        values = {}
        zip_list_ids = []
        res_provider_treatment = (
            request.env["geographical"]
            .sudo()
            .search([("zip_code", "=", zip_code)])
        )
        values["city"] = res_provider_treatment.city if res_provider_treatment.city else '' 
        values["state"] = res_provider_treatment.state if res_provider_treatment.state else ''
        values["id"] = res_provider_treatment.id
        zip_list_ids.append(values["id"])
        return values
    