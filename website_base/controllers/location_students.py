import requests
import json
from odoo import _, http
from odoo.http import request, route
from odoo.exceptions import ValidationError


class Location(http.Controller):
    
    @http.route("/add/location", type="http", website=True, auth="user", Methods=["POST"])
    def add_location(self, **kw):
        res_partner_id = request.env.user.partner_id
        values = {}
        max_hardship_zipcodes = request.env.company.max_hardship_zipcodes
        normal_number_zipcodes = request.env.company.normal_number_zipcodes
        hardship_id = request.env["hardship.request"].sudo().search([
            ('student_id', '=', res_partner_id.id),
        ], limit=1, order="id desc")
        if request.httprequest.method == "GET":
    
            values["partner"] = res_partner_id
            values["hardship"] = hardship_id
            if hardship_id.state == 'approved':
                can_apply_hardship = max_hardship_zipcodes or 3
            else:
                can_apply_hardship = normal_number_zipcodes or 5
            values.update({
                'rw': can_apply_hardship
            })
            return request.render("website_base.locations_students_template", values)
        elif request.httprequest.method == "POST":
            zip_code_list = []
            list_locations = []
            for x in range(int(kw.get('variable'))):
                val_id =  "id_%s" % (x)
                val_zip= "zip_%s" % (x)

                list_locations.append(int(kw.get(val_id)))
                zip_code_list.append(int(kw.get(val_zip)))
            print(list_locations)
            values = {
                "preferred_geographical_ids": [(0,0, {
                    'geographical_id': i,
                }) for i in list_locations],
                "is_reach_maximum_zip_code": True,
            }
            try:
                request_dummy = request.env["res.partner"].sudo().new(values)  
                request_dummy._check_geographical_ids()
                res_partner_id.sudo().write(values)
                template = request.env.ref('clinical_decision_making.mail_template_send_preferred_addresses_added')
                template.sudo().send_mail(request.env.user.id, force_send=True)
                return request.redirect("/my/home")
            except ValidationError as msg:
                if hardship_id.state == 'approved':
                    can_apply_hardship = max_hardship_zipcodes or 3
                else:
                    can_apply_hardship = normal_number_zipcodes or 5
                values.update({
                    'rw': can_apply_hardship,
                    "locations_zips":  zip_code_list,
                })
                error = str(msg.args[0])
                if error:
                    values["error"] = error
                    return request.render("website_base.locations_students_template", values)
    
    @http.route(
        ["/show/locations"], type="json", auth="user", methods=['POST'], website=True, csrf=False
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
    