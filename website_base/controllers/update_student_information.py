from odoo import http
from odoo.http import request
import base64


class UpdateInformation(http.Controller):

    @http.route("/update/attachment/student", type="http", website=True, auth="user", Methods=["POST"])
    def update_inforamtion(self, **kw):
        partner_id = request.env.user.partner_id
        id = kw.get("attachment_type_id")
        attachment_type_id = request.env["attachment.type"].with_company(partner_id.company_id.id).search([('id','=', id)])
        attachment_staudent_line = partner_id.medical_attachment_ids.filtered(lambda x: x.attachment_type.id == attachment_type_id.id)
        if kw and request.httprequest.method == "POST":
            try:
                attachment_staudent_line.with_company(partner_id.company_id.id).write({
                    "state":  "under_review", 
                    'expiration_date': kw.get("expiration_date"),
                    "attachment_ids": [(0,0,{
                        "name": kw.get("datas").filename,
                        "datas": base64.b64encode(kw.get("datas", False).read()),
                    })],
                        
                                        
                })   
                return request.redirect("/my")
            except Exception as e:
                return request.render("website_base.error_request", {'exception': e})

    @http.route("/update/scce/attachment/student", type="http", website=True, auth="user", Methods=["POST"])
    def update_scce_inforamtion(self, **kw):
        partner_id = request.env.user.partner_id
        id = kw.get("attachment_type_id")
        scce_attachment_type_id = request.env["scce.attachment.type"].with_company(partner_id.company_id.id).search([('id','=', id)])
        scce_attachment_staudent_line = partner_id.scce_medical_attachment_ids.filtered(lambda x: x.scce_attachment_type.id == scce_attachment_type_id.id)
        if kw and request.httprequest.method == "POST":
            try:
                scce_attachment_staudent_line.with_company(partner_id.company_id.id).write({
                    "state":  "under_review", 
                    'expiration_date': kw.get("expiration_date"),
                    "attachment_ids": [(0,0,{
                        "name": kw.get("datas").filename,
                        "datas": base64.b64encode(kw.get("datas", False).read()),
                    })],
                        
                                        
                })   
                return request.redirect("/my")
            except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
            
    @http.route("/save/update/attachment/student", type="json", auth="user", methods=['POST'], website=True, csrf=False)
    def save_update_attachment_student(self, **post):
         try:
                partner_id = request.env.user.partner_id
                partner_id.sudo().write({
                    "home_address":  post.get("home_address") if post.get("home_address") else False,                    
                    "mobile": post.get("mobile") if post.get("mobile") else False,
                    "phone": post.get("phone") if post.get("phone") else False,
                    "personal_email_address": post.get("personal_email_address") if post.get("personal_email_address") else False,
                    "personal_phone": post.get("personal_phone") if post.get("personal_phone") else False,
                })
                return True
         except Exception as e:
                return False
            
    @http.route("/save/changes/information", type="json", auth="user", methods=['POST'], website=True, csrf=False)
    def save_changes_information(self, **post):
         try:
                partner_id = request.env.user.partner_id
                partner_id.sudo().write({
                    "home_address":  post.get("home_address") if post.get("home_address") else False,                    
                    "mobile": post.get("mobile") if post.get("mobile") else False,
                    "phone": post.get("phone") if post.get("phone") else False,
                    "personal_email_address": post.get("personal_email_address") if post.get("personal_email_address") else False,
                    "personal_phone": post.get("personal_phone") if post.get("personal_phone") else False,
                })
                return True
         except Exception as e:
                return False

    @http.route("/save/changes/information", type="json", auth="user", methods=['POST'], website=True, csrf=False)
    def save_changes_information(self, **post):
         try:
                partner_id = request.env.user.partner_id
                partner_id.sudo().write({
                    "home_address":  post.get("home_address") if post.get("home_address") else False,                    
                    "mobile": post.get("mobile") if post.get("mobile") else False,
                    "phone": post.get("phone") if post.get("phone") else False,
                    "personal_email_address": post.get("personal_email_address") if post.get("personal_email_address") else False,
                    "personal_phone": post.get("personal_phone") if post.get("personal_phone") else False,
                })
                return True
         except Exception as e:
                return False