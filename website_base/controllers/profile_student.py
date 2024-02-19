from odoo import http
from odoo.http import request
import base64


class ProfileStudent(http.Controller):
    @http.route('/profile/student/<int:id>', website=True, type='http', auth="user")
    def profile_student(self, id=None, facility_id=None, **kw):
        values = {}
        partner_id = request.env.user.partner_id
        student_id = request.env["res.partner"].sudo().search([("id", "=", id)])
        archive_ids = request.env['archive'].sudo().search([
            ('student_id', '=', student_id.id)
        ])
        
        scce_id = archive_ids.mapped("department_id").search([]).mapped("scce_ids").search([]).mapped("scce_id").search([("id", "=", partner_id.id)])
        values["student_id"] = student_id
        hardship_ids = request.env["hardship.request"].sudo().search([
                ('student_id', '=', student_id.id)])
        hardship_id = request.env["hardship.request"].sudo().search([
                ('student_id', '=', student_id.id)
            ], limit=1, order="id desc")
        attachment_type_id = request.env["attachment.type"].sudo().search([])
        values["hardship_ids"] = hardship_ids
        values["hardship_id"] = hardship_id
        values["archive_ids"] = archive_ids
        values["locations"] = student_id.geographical_ids
        values["medical_attachment_ids"] = student_id.medical_attachment_ids
        values["scce_medical_attachment_ids"] = student_id.scce_medical_attachment_ids
        values["attachment_type_id"] = attachment_type_id
        values["facility_id"] = request.session.get('facility_id', False)
        if partner_id.is_scce == True:
            scce_attachment_type_id = request.env["scce.attachment.type"].sudo().search([("scce_id", "=", scce_id.id)])
            values["scce_attachment_type_id"] = scce_attachment_type_id
            return request.render("website_base.student_profile_templates", values)
        elif partner_id.is_ci == True:
            scce_attachment_type_id = request.env["scce.attachment.type"].sudo().search([("scce_id", "=",  partner_id.id)])
            values["scce_attachment_type_id"] = scce_attachment_type_id
            return request.render("website_base.ci_student_profile_templates", values)
    
    @http.route("/confirm/attachment/scce/<int:id>/<int:student_id>", type="http", website=True, auth="user", Methods=["POST"])
    def confirm_attachment_scce(self, id=None, student_id=None, **post):
        student_ids = request.env["res.partner"].sudo().search([('id','=', student_id)])
        scce_attachment_type_id = request.env["scce.attachment.type"].with_company(student_ids.company_id.id).search([('id','=', id)])
        scce_attachment_staudent_line = student_ids.scce_medical_attachment_ids.filtered(lambda x: x.scce_attachment_type.id == scce_attachment_type_id.id)
        try:
            scce_attachment_staudent_line.with_company(student_ids.company_id.id).action_confirmed()  
            return request.redirect_query(
                    "/profile/student/%s" % student_ids.id)
        except Exception as e:
            return request.render("website_base.error_request", {'exception': e})
        
    @http.route("/cancel/attachment/scce/<int:id>/<int:student_id>", type="http", website=True, auth="user", Methods=["POST"])
    def cancel_attachment_scce(self, id=None, student_id=None, **post):
        student_ids = request.env["res.partner"].sudo().search([('id','=', student_id)])
        scce_attachment_type_id = request.env["scce.attachment.type"].with_company(student_ids.company_id.id).search([('id','=', id)])
        scce_attachment_staudent_line = student_ids.scce_medical_attachment_ids.filtered(lambda x: x.scce_attachment_type.id == scce_attachment_type_id.id)
        try:
            scce_attachment_staudent_line.with_company(student_ids.company_id.id).action_cancel()  
            return request.redirect_query(
                    "/profile/student/%s" % student_ids.id)
        except Exception as e:
            return request.render("website_base.error_request", {'exception': e})
        
    @http.route("/update/attachment/scce/<int:id>/<int:student_id>", type="http", website=True, auth="user", Methods=["POST"])
    def update_required_attachment_scce(self, id=None, student_id=None, **post):
        student_ids = request.env["res.partner"].sudo().search([('id','=', student_id)])
        scce_attachment_type_id = request.env["scce.attachment.type"].with_company(student_ids.company_id.id).search([('id','=', id)])
        scce_attachment_staudent_line = student_ids.scce_medical_attachment_ids.filtered(lambda x: x.scce_attachment_type.id == scce_attachment_type_id.id)
        try:
            scce_attachment_staudent_line.with_company(student_ids.company_id.id).action_required_update()  
            return request.redirect_query(
                    "/profile/student/%s" % student_ids.id)
        except Exception as e:
            return request.render("website_base.error_request", {'exception': e})
        
    @http.route("/under_review/attachment/scce/<int:id>/<int:student_id>", type="http", website=True, auth="user", Methods=["POST"])
    def under_review_attachment_scce(self, id=None, student_id=None, **post):
        student_ids = request.env["res.partner"].sudo().search([('id','=', student_id)])
        scce_attachment_type_id = request.env["scce.attachment.type"].with_company(student_ids.company_id.id).search([('id','=', id)])
        scce_attachment_staudent_line = student_ids.scce_medical_attachment_ids.filtered(lambda x: x.scce_attachment_type.id == scce_attachment_type_id.id)
        try:
            scce_attachment_staudent_line.with_company(student_ids.company_id.id).action_under_review()  
            return request.redirect_query(
                    "/profile/student/%s" % student_ids.id)
        except Exception as e:
            return request.render("website_base.error_request", {'exception': e})
        