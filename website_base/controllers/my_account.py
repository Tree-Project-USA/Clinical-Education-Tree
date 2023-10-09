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
        res_partner_id = request.env.user.partner_id
        return request.render("website_base.user_profile_templates", {'partner': res_partner_id})
    
    @http.route("/add/location", type="http", website=True, auth="user", Methods=["POST"])
    def add_location(self, **kw):
        res_partner_id = request.env.user.partner_id
        if kw and request.httprequest.method == "POST":
            data = json.loads(kw["data_line_ids"])
            val = [(0, 0, line) for line in data]
            values = {
                "locatio_ids": val,
                "is_reach_maximum_zip_code": True,
            }
            try:
                lists = []
                for line in data:
                    if line["zip"] in lists:
                       raise ValidationError(_("zip code is define before please zip code must be non-dublicate"))
                    else:
                        lists.append(line["zip"])
                request_dummy = request.env["res.partner"].sudo().new(values)  
                request_dummy.check_zip_code_distance(lists)
                res_partner_id.sudo().write(values)
                return request.redirect("/my/home")
            except ValidationError as msg:
                values.update(kw)
                error = str(msg.args[0])
                if error:
                    kw["error"] = error
        value = kw 
        if res_partner_id.can_apply_hardship:
            can_apply_hardship = 3
        else:
            can_apply_hardship = 5
        value.update({
            'rw': can_apply_hardship
        })
        return request.render("website_base.locations_students_template", value)
    
    @http.route(['/get/locstion/infor'], type='json', auth="public", methods=['POST'], website=True)
    def get_locstion_infor(self,**post):
        zip = post.get('post')
        token = self.env['ir.config_parameter'].sudo(
        ).get_param('zip_code_token')
        if token:
            token= 'DemoOnly00gH8wbb344Ca9wRlS2B9Btt3Nqg7g6GkvvSswAhCSX2jtqxzmK8kWuM'
            url = "https://www.zipcodeapi.com/rest/%s/info.json/%s/degrees" % (token, zip)
            res = requests.get(url)
            if res.status_code == 200:
                return res.json()
        else:
            return False


    
    
