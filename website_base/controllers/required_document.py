from odoo import http
from odoo.http import request

class RequiredDocument(http.Controller):

    @http.route("/required/documents", type="http", website=True, auth="user")
    def required_documents(self):
        values = {}
        values["student_id"] = request.session.get('student_id', False)
        return request.render("website_base.required_document_template", values)
    
    @http.route("/create/required/documents", type="http", website=True, auth="user", Methods=["POST"])
    def create_required_documents(self, **kw):
        partner_id = request.env.user.partner_id
        try:
            for document in range(0, int(kw.get("len_type_documents"))):
                values = {
                    'scce_id': partner_id.id,
                    'name': kw.get("name_" + str(document)),
                    'portal_id': kw.get("portal_id_" + str(document)),
                    'description': kw.get("description_" + str(document)),
                }
                request.env["scce.attachment.type"].sudo().create(values)
            return request.redirect("/success/required/document")
        except Exception as e:
            return request.render("website_base.error_request", {'exception': e})
       
    @http.route("/success/required/document", type="http", website=True, auth="user")
    def success_required_document(self):
        return request.render("website_base.success_required_document")
