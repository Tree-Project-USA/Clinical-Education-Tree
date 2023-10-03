import base64
from datetime import datetime
import json
from odoo import _, http
from odoo.http import request, route
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import CustomerPortal

# class CustomAccount(CustomerPortal):
#     @route(["/my/account"], type="http", auth="user", website=True)
#     def account(self, redirect=None, **post):
#         values = {}
#         if request.httprequest.method == "GET":
#             partner = request.env.user.partner_id
#             values.update(dict(request.params))
#             countries = request.env["res.country"].sudo().search([])
#             states = request.env["res.country.state"].sudo().search([])
#             citys = request.env["res.city"].sudo().search([])
#             values.update({
#                 "partner": partner,
#                 "countries": countries,
#                 "states": states,
#                 "citys": citys,
#                 "has_check_vat": hasattr(request.env["res.partner"], "check_vat"),
#                 "redirect": redirect,
#                 "page_name": "my_details",
#             })

#         if post and request.httprequest.method == "POST":
#             try:
#                 update_inforamtion = {
#                     "name": post.get("name"),
#                     "email": post.get("email"),
#                     "mobile": post.get("mobile"),
#                     "street": post.get("street"),
#                     "country_id": int(post.get("country_id")),
#                     "state_id": post.get("state_id"),
#                     "city_id": post.get("city_id"),
#                 }
#                 partner.sudo().write(
#                     update_inforamtion
#                 )
#                 values.update(
#                     {
#                         "success": (_("تم تعديل معلوماتك بنجاح"))
#                     }
#                 )
#             except Exception as e:
#                 values.update(
#                     {
#                         "error_message": (_("حدث خطاء في إدخال المعلومات"))
#                     }
#                 )
#                 return values
#         response = request.render("website_base.locations_students_template", values)
#         response.headers["X-Frame-Options"] = "DENY"
#         return response
        
#     @route(["/user/profile"], type="http", auth="user", website=True)
#     def user_profile(self, redirect=None, **post):
#         value={}
#         partner = request.env.user.partner_id
#         value["partner_id"] = partner
#         return request.render("website_base.user_profile_templates", value)
    

class CustomerPortals(CustomerPortal):
    # @route(["/my", "/my/home"], type="http", auth="user", website=True)
    # def home(self, **kw):
    #     return request.redirect("/my/home")
        
    @route([])
    def home(self):
        # values = {}
        res_partner_id = request.env.user.partner_id
        # values["partner"] = res_partner_id 
        return request.render("website_base.user_profile_templates", {'partner': res_partner_id})
    
    @http.route("/add/location", type="http", website=True, auth="user", Methods=["POST"])
    def add_location(self, **kw):
        res_partner_id = request.env.user.partner_id
        # params = {}
        if kw and request.httprequest.method == "POST":
            data = json.loads(kw["data_line_ids"])
            val = [(0, 0, line) for line in data]
            values = {
                "locatio_ids": val,
                "is_reach_maximum_zip_code": True,
            }
            try:
                # request_dummy = request.env["res.partner"].sudo().new(values)  
                res_partner_id.locatio_ids._check_product_uom_category_id()
                print('=====================================33333333333333333333333333=================')
                # res_partner_id.sudo().write(values)
            except ValidationError as msg:
                values.update(kw)
                error = str(msg.args[0])
                if error:
                    kw["error"] = error
        value = kw 
        can_apply_hardship = res_partner_id.can_apply_hardship
        value.update({
            # 'partner': res_partner_id,
            'rw': 3
        })
        print(kw)
        print(value)
        return request.render("website_base.locations_students_template", value)
    
    
    
