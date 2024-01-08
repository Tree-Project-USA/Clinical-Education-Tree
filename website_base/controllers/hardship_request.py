from odoo import http
from odoo.http import request
# from odoo.tools import image_resize_images

import base64
import werkzeug


class CustomerPortals(http.Controller):

    @http.route('/download_attachment', type='http', auth="public")
    def download_attachment(self, **kwargs):
        attachment_id = int(kwargs.get('id', 0))
        attachment = request.env['res.config.settings'].sudo().browse(attachment_id)

        print(attachment)
        print(attachment.hardship_form_attachment)
        if attachment.hardship_form_attachment:
            print("ahmed")
            filecontent = base64.b64decode(attachment.hardship_form_attachment)
            headers = [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', werkzeug.urls.url_quote(attachment.name))
            ]
            return request.make_response(filecontent, headers)
        else:
            print("salim")
            return request.not_found()
        
    @http.route("/hardship/request", type="http", website=True, auth="user")
    def hardship_request(self):
        values = {}
        partner_id = request.env.user.partner_id
        
        hardship_id = request.env["res.prtner"].sudo().search([
            ('student_id', '=', partner_id.id),
            ], limit=1, order="id desc")
        
        hardship_id = request.env["hardship.request"].sudo().search([
            ('student_id', '=', partner_id.id),
            ], limit=1, order="id desc")
        company_id = request.env['res.company'].sudo().search([])
        print(company_id.background_image)
        # hardship_form_attachment = request.env['ir.config_parameter'].sudo(
        #         ).get_param('hardship_form_attachment')
        # print(hardship_form_attachment)
        # values["hardship_form_attachment"] = hardship_form_attachment
        values["company_id"] =  company_id
        if hardship_id and hardship_id.state not in ["declined", "expired"]:
            return request.redirect("/my/home")
        return request.render("website_base.hardship_request_template", values)
    
    @http.route("/create/hardship/request", type="http", website=True, auth="user", Methods=["POST"])
    def create_hardship_request(self, **kw):
        partner_id = request.env.user.partner_id
        hardship_id = request.env["hardship.request"].sudo().search([
            ('student_id', '=', partner_id.id),
            ])
        if kw and request.httprequest.method == "POST":
            try:
                zip_code_list = []
                file_list = []
                for zip in range(0, int(kw.get("len_zip_code"))):
                    zip_code = request.env["geographical"].sudo().search([("zip_code", "=", kw.get("zip_code_" + str(zip)))])
                    zip_code_list.append(zip_code.id)
                hardship_id = request.env["hardship.request"].sudo().create(
                    {
                        "student_id": partner_id.id,
                        "note":  kw.get("note") if kw.get("note") else False,
                        "state": "initial_submission",
                        "geographical_ids": [(6, 0, zip_code_list)],
                    }
                )
                for files in range(0, int(kw.get("len_file"))):
                    line_file= (0,0,{
                        'name': kw.get("datas_" + str(files)).filename,
                        'datas': base64.b64encode(kw.get("datas_" + str(files), False).read()),
                        'res_model': 'hardship.request',
                        'res_id': hardship_id.id,
                    })
                    file_list.append(line_file)
                    
                hardship_id.sudo().write({
                    "attachment_ids": file_list,
                })
                partner_id.sudo().write({
                    "can_apply_hardship": True,
                })
                return request.redirect("/success/hardship/request")
            except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
    
    @http.route("/update/hardship/request", type="http", website=True, auth="user", Methods=["POST"])
    def update_hardship_request(self, hardship=None, **post):
        partner_id = request.env.user.partner_id
        hardship_id = request.env["hardship.request"].sudo().search([
            ('student_id', '=', partner_id.id),
            ('state', '=', 'update_required')
            ], limit=1, order="id desc")
        if post and request.httprequest.method == "POST":
            try:
                zip_code_list = []
                file_list = []
                for zip in range(0, int(post.get("len_zip_code"))):
                    zip_code = request.env["geographical"].sudo().search([("zip_code", "=", post.get("zip_code_" + str(zip)))])
                    zip_code_list.append(zip_code.id)
                
                for files in range(0, int(post.get("len_file"))):
                    line_file= (0,0,{
                        'name': post.get("datas_" + str(files)).filename,
                        'datas': base64.b64encode(post.get("datas_" + str(files), False).read()),
                        'res_model': 'hardship.request',
                        'res_id': hardship_id.id,
                    })
                    file_list.append(line_file)
                hardship_id.sudo().write({
                    "note":  post.get("note") if post.get("note") else False,                    
                    "state": "under_review",
                    "attachment_ids": file_list,
                    "geographical_ids": [(6, 0, zip_code_list)],
                })
                    
                return request.redirect("/success/hardship/request")
            except Exception as e:
                return request.render("website_base.error_request", {'exception': e})
        if hardship_id:
            return request.render("website_base.update_hardship_request_template",{'hardship_id': hardship_id})
        else:
            return request.redirect("/my/home")
    
    @http.route("/success/hardship/request", type="http", website=True, auth="user")
    def success_hardship_request(self):
        return request.render("website_base.success_request_template")
    
    @http.route("/info/hardship/request", type="http", website=True, auth="user")
    def info_hardship_request(self):
        values = {}
        partner_id = request.env.user.partner_id
        values["locations"] = partner_id.geographical_ids
        return request.render("website_base.locations_students_info_template", values)
