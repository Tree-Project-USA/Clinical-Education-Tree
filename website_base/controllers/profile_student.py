from odoo import http
from odoo.http import request


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
        attachment_request_id = request.env["attachment.request"].sudo().search([
                ('student_id', '=', student_id.id)
            ], limit=1, order="id desc")
        scce_medical_attachment_id = request.env["scce.attachment.request"].sudo().search([
                ('student_id', '=', student_id.id)
            ], order="id desc")
        attachment_type_id = request.env["attachment.type"].sudo().search([])
        values["hardship_ids"] = hardship_ids
        values["hardship_id"] = hardship_id
        values["archive_ids"] = archive_ids
        values["locations"] = student_id.geographical_ids
        values["medical_attachment_id"] = attachment_request_id
        values["scce_medical_attachment_id"] = scce_medical_attachment_id
        values["attachment_type_id"] = attachment_type_id
        values["facility_id"] = request.session.get('facility_id', False)
        if partner_id.is_scce == True:
            scce_attachment_type_id = request.env["scce.attachment.type"].sudo().search([("scce_id", "=", scce_id.id)])
            values["scce_attachment_type_id"] = scce_attachment_type_id
            return request.render("website_base.student_profile_templates", values)
        elif partner_id.is_ci == True:
            scce_attachment_type_id = request.env["scce.attachment.type"].sudo().search([("scce_id", "=",  partner_id.scce_id.id)])
            values["scce_attachment_type_id"] = scce_attachment_type_id
            return request.render("website_base.ci_student_profile_templates", values)
    
    @http.route("/confirm/attachment/scce/<int:id>", type="http", website=True, auth="user", Methods=["POST"])
    def confirm_attachment_scce(self, id=None, **post):
        scce_attachment_request = request.env["scce.attachment.request"].sudo().search([("student_id", "=", id),("state", "=", 'under_review')])
        print(scce_attachment_request)
        try:
            scce_attachment_request.confirm_attachment()
            scce_attachment_request.sudo().write({
                "state": 'confirmed',                    
            })
            return request.redirect_query(
                        "/profile/student/%s" % id)
        except Exception as e:
            return request.render("website_base.error_request", {'exception': e})
        
    @http.route("/confirm/attachment/scce/<int:id>", type="http", website=True, auth="user", Methods=["POST"])
    def confirm_attachment_scce(self, id=None, **post):
        scce_attachment_request = request.env["scce.attachment.request"].sudo().search([("id", "=", id)])
        print(scce_attachment_request.student_id)
        try:
            scce_attachment_request.confirm_attachment()
            return request.redirect_query(
                        "/profile/student/%s" % scce_attachment_request.student_id.id)
        except Exception as e:
            return request.render("website_base.error_request", {'exception': e})
        
    @http.route("/cancel/attachment/scce/<int:id>", type="http", website=True, auth="user", Methods=["POST"])
    def cancel_attachment_scce(self, id=None, **post):
        scce_attachment_request = request.env["scce.attachment.request"].sudo().search([("id", "=", id)])
        try:
            scce_attachment_request.action_cancel()
            return request.redirect_query(
                        "/profile/student/%s" % scce_attachment_request.student_id.id)
        except Exception as e:
            return request.render("website_base.error_request", {'exception': e})
        
    @http.route("/update/attachment/scce/<int:id>", type="http", website=True, auth="user", Methods=["POST"])
    def update_required_attachment_scce(self, id=None, **post):
        scce_attachment_request = request.env["scce.attachment.request"].sudo().search([("id", "=", id)])
        try:
            scce_attachment_request.action_update_required()
            return request.redirect_query(
                        "/profile/student/%s" % scce_attachment_request.student_id.id)
        except Exception as e:
            return request.render("website_base.error_request", {'exception': e})
        
    @http.route("/under_review/attachment/scce/<int:id>", type="http", website=True, auth="user", Methods=["POST"])
    def under_review_attachment_scce(self, id=None, **post):
        scce_attachment_request = request.env["scce.attachment.request"].sudo().search([("id", "=", id)])
        try:
            scce_attachment_request.action_under_review()
            return request.redirect_query(
                        "/profile/student/%s" % scce_attachment_request.student_id.id)
        except Exception as e:
            return request.render("website_base.error_request", {'exception': e})
        