import base64
import json
from odoo import http
from odoo.http import request


class CustomerPortals(http.Controller):


    @http.route("/hardship/request", type="http", website=True, auth="user")
    def hardship_request(self):
        return request.render("website_base.hardship_request_template")
    
    @http.route("/update/hardship/request", type="http", website=True, auth="user", Methods=["POST"])
    def update_hardship_request(self, hardship=None, **post):
        partner_id = request.env.user.partner_id
        hardship_id = request.env["hardship.request"].sudo().search([
            ('student_id', '=', partner_id.id),
            ('state', '=', 'update')
            ])
        if post and request.httprequest.method == "POST":
            try:
                zip_code_list_h = [int(i) for i in post.get('list_zip_code_h_u').split(",") if i != ','] if post.get('list_zip_code_h_u', False) else []
                file_list = []
                for files in range(0, int(post.get("len_file"))):
                    line= (0,0,{
                        'name': post.get("datas_" + str(files)).filename,
                        'datas': base64.b64encode(post.get("datas_" + str(files), False).read()),
                    })
                file_list.append(line)
                hardship_id.attachment_ids.unlink()
                hardship_id.sudo().write({
                    "note":  post.get("note") if post.get("note") else False,
                    "attachment_ids": file_list,
                    "state": "draft",
                    "geographical_ids": [(6, 0, zip_code_list_h)],
                })
                return request.redirect("/success/hardship/request")
            except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
        if hardship_id:
            return request.render("website_base.update_hardship_request_template",{'hardship_id': hardship_id})
        else:
            return request.redirect("/my/home")

    @http.route("/create/hardship/request", type="http", website=True, auth="user", Methods=["POST"])
    def create_hardship_request(self, **kw):
        partner_id = request.env.user.partner_id
        if kw and request.httprequest.method == "POST":
            try:
                zip_code_list_h = [int(i) for i in kw.get('list_zip_code_h').split(",") if i != ','] if kw.get('list_zip_code_h', False) else []
                file_list = []
                for files in range(0, int(kw.get("len_file"))):
                    line= (0,0,{
                        'name': kw.get("datas_" + str(files)).filename,
                        'datas': base64.b64encode(kw.get("datas_" + str(files), False).read()),
                    })
                    file_list.append(line)
                HardshipRequest = request.env["hardship.request"].sudo().create(
                    {
                        "student_id": partner_id.id,
                        "note":  kw.get("note") if kw.get("note") else False,
                        "attachment_ids": file_list,
                        "state": "draft",
                        "geographical_ids": zip_code_list_h,
                    }
                )
                partner_id.sudo().write({
                    "can_apply_hardship": True,
                })
                template = request.env.ref('website_base.mail_template_send_hardship_request')
                template.sudo().send_mail(HardshipRequest.id, force_send=True)
                return request.redirect("/success/hardship/request")
            except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
    
    @http.route("/success/hardship/request", type="http", website=True, auth="public")
    def success_hardship_request(self):
        return request.render("website_base.success_request_template")
    
    @http.route("/info/hardship/request", type="http", website=True, auth="public")
    def info_hardship_request(self):
        values = {}
        partner_id = request.env.user.partner_id
        values["locations"] = partner_id.geographical_ids
        return request.render("website_base.locations_students_info_template", values)