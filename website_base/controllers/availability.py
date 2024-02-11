from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError

class SubmitAvailability(http.Controller):
    @http.route('/submit/availability', website=True, type='http', auth="user")
    def submit_availability(self, id=None, **kw):
        values = {}
        partner_id = request.env.user.partner_id
        if request.httprequest.method == "GET":
            values["partner_id"] = partner_id 
            return request.render("website_base.availability_template", values)
        elif request.httprequest.method == "POST":
            def create_line_ids(department, kw):
                return (0, 0, {
                'department_id': kw[f"department_id_{department}"],
                'experience_id': kw[f"experience_id_{department}"],
                'placement_term': kw[f"placement_term_{department}"],
                'company_id': kw[f"company_id_{department}"],
                'year': kw[f"term_{department}"],
                'setting': kw[f"setting_{department}"],
                'offers': kw[f"offers_{department}"],
            })
            department_list = []
            f_list = []
            for department in range(int(kw.get("len_department"))):
                department_id = request.env["facility.department"].sudo().search([("id", "=", kw[f"department_id_{department}"])])
                facility_id = department_id.mapped("facility_id").id

                if facility_id not in f_list:
                    if f_list:
                        f_list.pop(0)
                        department_list = []

                    f_list.append(facility_id)
                    line_ids = create_line_ids(department, kw)
                    department_list.append(line_ids)
                    vals = {
                        "facility_id": facility_id,
                        "line_ids": department_list,
                    }
                    placement_offer_request = request.env["placement.offer"].sudo().create(vals)
                else:
                    line_ids = create_line_ids(department, kw)
                    department_list = [line_ids]
                    placement_offer_request.sudo().write({
                        "line_ids": department_list,
                    })

            return request.render("website_base.success_placement_offer_template")
        
    @http.route('/facility/placement/offer/<int:id>', website=True, type='http', auth="user")
    def facility_placement_offer(self, id=None, **kw):
        partner_id = request.env.user.partner_id
        if request.httprequest.method == "GET":
            facility_id = request.env["medical.facility"].sudo().search([("id", "=", id)])
            archive_ids = request.env['archive'].sudo().search([
                ('facility_id', '=', facility_id.id), 
            ])
            values = {
                "department_ids": facility_id.mapped("department_ids").filtered(lambda q: partner_id.id in q.scce_ids.mapped('scce_id').ids),
                "scce_ids": facility_id.mapped("scce_ids"),
                "placement_history_ids": facility_id.mapped("archive_ids"),
                "partner_id": partner_id ,
                "facility_id": facility_id ,
                "archive_ids": archive_ids,
            }
            values.update(dict(request.params))
            dict(request.params)
            request.session['facility_id'] =  facility_id.id
            return request.render("website_base.show_placement_offer_facility_template", values)
        
    @http.route('/confirm/student/<int:id>', website=True, type='http', auth="user")
    def confirm_student(self, id=None, **kw):
        facility_id = request.session.get('facility_id', False)
        archive_id = request.env['archive'].sudo().search([
            ('id', '=', id),
        ])
        archive_id.sudo().write({
            "placement_status": "confirmed",
            "is_show_portal": True,
        })
        archive_id.archive_offer_id.write({
            "active": True,
        })
        return request.redirect_query(
                            "/facility/placement/offer/%s" % facility_id)
        
    @http.route('/declin/eassigned/student/<int:id>', website=True, type='http', auth="user")
    def declin_assigned_student(self, id=None, **kw):
        facility_id = request.session.get('facility_id', False)
        archive_id = request.env['archive'].sudo().search([
            ('id', '=', id),
        ])
        archive_id.sudo().write({
            "placement_status": "decline",
            "is_show_portal": True,
            "main_offer_student_id": archive_id.student_id.id,
        })
        archive_id.archive_offer_id.write({
            "active": True,
        })
        return request.redirect_query("/facility/placement/offer/%s" % facility_id)
        
    @http.route('/cancel/eassigned/student/<int:id>', website=True, type='http', auth="user")
    def cancel_assigned_student(self, id=None, **kw):
        facility_id = request.session.get('facility_id', False)
        archive_id = request.env['archive'].sudo().search([
            ('id', '=', id),
        ])
        archive_id.sudo().write({
            "placement_status": "not_placed",
            "is_show_portal": True,
            "main_offer_student_id": archive_id.student_id.id,
        })
        print(archive_id.archive_offer_id)
        archive_id.archive_offer_id.write({
            "active": False,
        })
        return request.redirect_query("/facility/placement/offer/%s" % facility_id)
        
    @http.route('/replay/student/<int:id>', website=True, type='http', auth="user")
    def reaplay_assigned_student(self, id=None, **kw):
        facility_id = request.session.get('facility_id', False)
        archive_id = request.env['archive'].sudo().search([
            ('id', '=', id),
        ])
        if archive_id.main_offer_student_id == archive_id.archive_offer_id.student_id:
            archive_id.sudo().write({
                "active": True,
                "placement_status": "pending",
            })
            return request.redirect_query("/facility/placement/offer/%s" % facility_id)
        elif not archive_id.archive_offer_id.student_id:
            archive_id.sudo().write({
                "active": True,
                "placement_status": "pending",
            })
            return request.redirect_query("/facility/placement/offer/%s" % facility_id)
        else:
            # TODO: Add code here when avalible other offer student
            error = _("This placement offer has been taken by other student")
            return request.redirect_query("/facility/placement/offer/%s" % facility_id, {"error": error})
        
    @http.route('/profile/student/<int:id>', website=True, type='http', auth="user")
    def profile_student(self, id=None, facility_id=None, **kw):
        values = {}
        student_id = request.env["res.partner"].sudo().search([("id", "=", id)])
        values["student_id"] = student_id
        hardship_ids = request.env["hardship.request"].sudo().search([
                ('student_id', '=', student_id.id)])
        hardship_id = request.env["hardship.request"].sudo().search([
                ('student_id', '=', student_id.id)
            ], limit=1, order="id desc")
        archive_ids = request.env['archive'].sudo().search([
                ('student_id', '=', student_id.id), 
            ])
        attachment_request_id = request.env["attachment.request"].sudo().search([
                ('student_id', '=', student_id.id)
            ], limit=1, order="id desc")
        values["hardship_ids"] = hardship_ids
        values["hardship_id"] = hardship_id
        values["archive_ids"] = archive_ids
        values["locations"] = student_id.geographical_ids
        values["medical_attachment_id"] = attachment_request_id
        values["facility_id"] = request.session.get('facility_id', False)
        return request.render("website_base.student_profile_templates", values)
    
    @http.route('/departments', website=True, type='json', auth="user", csrf=False)
    def departments(self, id=None, **kw):
        values = {}
        department_ids = request.env["facility.department"].sudo().search([])
        company_ids = request.env["res.company"].sudo().search([])
        clinical_experience_ids = request.env["clinical.experience"].sudo().search([])
        SELECTION_YEAR_RANGE = [{
                    'id': str(i),
                } for i in range(2020, 2500)]
        departments = [{
                    'id': department.id,
                    'name': department.name if department.name else '',
                    'street': department.street if department.street else '',
                    'city': department.city if department.city else '',
                    'state': department.state if department.state else '',
                } for department in department_ids]
        companys = [{
                    'id': company.id,
                    'name': company.name if company.name else '',
                } for company in company_ids]
        experiences = [{
                    'id': experience.id,
                    'name': experience.name if experience.name else '',
                } for experience in clinical_experience_ids]
        values["department_ids"] = departments
        values["company_ids"] = companys
        values["clinical_experience_ids"] = experiences
        values["SELECTION_YEAR_RANGE"] = SELECTION_YEAR_RANGE
        return values