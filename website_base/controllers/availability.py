from odoo import http, _, SUPERUSER_ID
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
                        "scce_id": partner_id.id,
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
        
    @http.route('/facility/scce/placement/offer/<int:id>', website=True, type='http', auth="user")
    def facility_scce_placement_offer(self, id=None, **kw):
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
                "ci_id": facility_id.mapped("ci_ids")
            }
            values.update(dict(request.params))
            dict(request.params)
            request.session['facility_id'] =  facility_id.id
            return request.render("website_base.show_scce_placement_offer_facility_template", values)
        
    @http.route('/facility/ci/placement/offer/<int:id>', website=True, type='http', auth="user")
    def facility_ci_placement_offer(self, id=None, **kw):
        partner_id = request.env.user.partner_id
        if request.httprequest.method == "GET":
            facility_id = request.env["medical.facility"].sudo().search([("id", "=", id)])
            facility_department_id = request.env["facility.department"].sudo().search([("facility_id", "=", facility_id.id)])
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
                "facility_department_id": facility_department_id,
            }
            values.update(dict(request.params))
            dict(request.params)
            request.session['facility_id'] =  facility_id.id
            return request.render("website_base.show_ci_placement_offer_facility_template", values)
        
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
                            "/facility/scce/placement/offer/%s" % facility_id)
        
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
        return request.redirect_query("/facility/scce/placement/offer/%s" % facility_id)
        
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
        archive_id.archive_offer_id.write({
            "active": False,
        })
        return request.redirect_query("/facility/scce/placement/offer/%s" % facility_id)
        
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
            return request.redirect_query("/facility/scce/placement/offer/%s" % facility_id)
        elif not archive_id.archive_offer_id.student_id:
            archive_id.sudo().write({
                "active": True,
                "placement_status": "pending",
            })
            return request.redirect_query("/facility/scce/placement/offer/%s" % facility_id)
        else:
            # TODO: Add code here when avalible other offer student
            error = _("This placement offer has been taken by other student")
            return request.redirect_query("/facility/scce/placement/offer/%s" % facility_id, {"error": error})
    
    @http.route('/departments', website=True, type='json', auth="user", csrf=False)
    def departments(self, id=None, **kw):
        values = {}
        user_id = request.env.user.company_ids
        print(user_id)
        company_ids = request.env.user.company_ids
        SELECTION_YEAR_RANGE = [{
                    'id': str(i),
                } for i in range(2020, 2500)]
        companys = [{
                    'id': company.id,
                    'name': company.name if company.name else '',
                } for company in company_ids]
        values["company_ids"] = companys
        values["SELECTION_YEAR_RANGE"] = SELECTION_YEAR_RANGE
        return values
    
    @http.route('/inforamtion/company', website=True, type='json', auth="user", csrf=False)
    def information_company(self, company_id=None, **kw):
        values = {}
        partner_id = request.env.user.partner_id
        print(company_id)
        print(company_id)
        print(company_id)
        company_id = request.env["res.company"].sudo().search([("id", "=", company_id)])
        department_ids = request.env["facility.department"].sudo().search([("company_id", "=", company_id.id), ('scce_ids.scce_id', '=', partner_id.id)])
        print(company_id)
        print(department_ids)
        clinical_experience_ids = request.env["clinical.experience"].search([("company_id", "=", company_id.id)])
        experiences = [{
                    'id': experience.id,
                    'name': experience.name if experience.name else '',
                } for experience in clinical_experience_ids]
        departments = [{
                    'id': department.id,
                    'name': department.name if department.name else '',
                    'street': department.street if department.street else '',
                    'city': department.city if department.city else '',
                    'state': department.state if department.state else '',
                } for department in department_ids]
        values["clinical_experience_ids"] = experiences
        values["department_ids"] = departments
        return values
    
    @http.route('/clinical/experience/dates', website=True, type='json', auth="user", csrf=False)
    def clinical_experience_dates(self, years= None, **kw):
        values = {}
        clinical_experience_dates_ids = request.env['clinical.experience.dates'].search([("year", "=", years)])
        clinical_experience = clinical_experience_dates_ids.mapped("experience_id")
        experiences = [{
                    'id': experience.id,
                    'name': experience.name if experience.name else '',
                } for experience in clinical_experience]
        values["clinical_experience_ids"] = experiences
        return values
        
    @http.route('/program/experience/term', website=True, type='json', auth="user", csrf=False)
    def program_experience_term(self, years=None, experience_id=None, terms=None, **kw):
        values = {}
        start_date = ""
        end_date = ""
        print(terms, "termstermstermsterms")
        
        print(experience_id)
        clinical_experience_ids = request.env['clinical.experience'].sudo().search([("id", "=", experience_id)])
        print(clinical_experience_ids.mapped("date_ids"))
        for i in clinical_experience_ids.mapped("date_ids"):
            if i.year == years:
                if terms == "fall":
                    start_date = i.fa_start_date if i.fa_start_date else ""
                    end_date = i.fa_end_date if i.fa_end_date else ""
                elif terms == "spring":
                    start_date = i.sp_start_date if i.sp_start_date else ""
                    end_date = i.sp_end_date if i.sp_end_date else ""
                elif terms == "summer":
                    start_date = i.su_start_date if i.su_start_date else ""
                    end_date = i.su_end_date if i.su_end_date else ""
            else:
                break
            values["start_date"] = start_date 
            values["end_date"] = end_date 
            return values
        