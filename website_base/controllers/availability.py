from odoo import http, _, SUPERUSER_ID, Command
from odoo.http import request
from odoo.exceptions import ValidationError

class SubmitAvailability(http.Controller):
    @http.route('/submit/availability', website=True, type='http', auth="user")
    def submit_availability(self, id=None, **post):
        values = {}
        partner_id = request.env.user.partner_id
        if request.httprequest.method == "GET":
            values["partner_id"] = partner_id 
            company_ids = request.env.user.company_ids
            SELECTION_YEAR_RANGE = [{
                        'id': str(i),
                    } for i in range(2020, 2500)]
            values["company_ids"] = company_ids
            values["SELECTION_YEAR_RANGE"] = SELECTION_YEAR_RANGE
            return request.render("website_base.availability_template", values)
        elif request.httprequest.method == "POST" and post:
            departments = post.get("line_department_list").split(",")
            placement_term = post.get("placement_term_list").split(",")
            experience_ids = post.get("experience_id_list").split(",")
            ce_dict = {}
            for ce in experience_ids:
                list_ce = ce.split("_")
                if list_ce[0] in ce_dict:
                    
                    ce_dict.get(list_ce[0]).append(int(list_ce[1]))
                else:
                    ce_dict[list_ce[0]] = [int(list_ce[1])]
                
            list_departments = [int(i) for i in departments]    
            for term in placement_term:
                for index, department in enumerate(list_departments):
                    res_department = request.env['facility.department'].sudo().search([ ('id', '=', department)])
                    placement_offer = request.env['placement.offer'].with_company(request.env.user.company_id).\
                     search([
                         ('state', '=', 'offer_details_entered'),
                         ('scce_id', '=', partner_id.id),
                         ('facility_id', '=', res_department.facility_id.id),
                         ],limit=1, order='create_date desc')
                    if placement_offer :
                        request.env['placement.offer.line'].sudo().create({
                            'department_id': res_department.id,
                                                'offer_id': placement_offer.id,
                                                'experience_id': [Command.set(ce_dict.get(term))],
                                                'placement_term': term,
                                                'company_id': int(post.get("company_id")),
                                                'year': post.get("year_term"),
                                                'setting': post.get("setting"),
                                                'offers': int(post[f"number_{index + 1}"]),
                        })
                       
                    else:
                        request.env["placement.offer"].sudo().create({
                            'scce_id': partner_id.id,
                            "facility_id": res_department.facility_id.id,
                            "line_ids":[
                                Command.create({
                                    'department_id': res_department.id,
                                    'experience_id': [Command.set(ce_dict.get(term))],
                                    'placement_term': term,
                                    'company_id': int(post.get("company_id")),
                                    'year': post.get("year_term"),
                                    'setting': post.get("setting"),
                                    'offers': int(post[f"number_{index + 1}"]),
                                })]     
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
    
    
    @http.route('/inforamtion/company', website=True, type='json', auth="user", csrf=False)
    def information_company(self, **post):
        values = {}
        partner_id = request.env.user.partner_id
        department_ids = request.env["facility.department"].sudo().search([('scce_ids.scce_id', '=', partner_id.id)])
        departments = [{
                    'id': department.id,
                    'name': department.name if department.name else '',
                    'street': department.street if department.street else '',
                    'city': department.city if department.city else '',
                    'state': department.state if department.state else '',
                } for department in department_ids]
        values["department_ids"] = departments
        return values
    
    @http.route('/clinical/experience/dates', website=True, type='json', auth="user", csrf=False)
    def clinical_experience_dates(self, **post):
        values = {}
        terms = post.get("placement_term")
        clinical_experience_dates_ids = request.env['clinical.experience.dates']\
            .search([("year", "=", post.get("year_term"))])
        experiences = []
        for  clinical in clinical_experience_dates_ids:
            for t in terms:
                if t == "fall":
                    start_date = clinical.fa_start_date if clinical.fa_start_date else ""
                    end_date = clinical.fa_end_date if clinical.fa_end_date else ""
                elif t == "spring":
                    start_date = clinical.sp_start_date if clinical.sp_start_date else ""
                    end_date = clinical.sp_end_date if clinical.sp_end_date else ""
                elif t == "summer":
                    start_date = clinical.su_start_date if clinical.su_start_date else ""
                    end_date = clinical.su_end_date if clinical.su_end_date else ""
                clinical_dict ={
                    'id': clinical.experience_id.id,
                    'name': clinical.experience_id.name if clinical.experience_id.name else '',
                    "start_date": start_date, 
                    "end_date" : end_date, 
                    "term" : t, 
                }
                experiences.append(clinical_dict)
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
                if "fall" in terms:
                    start_date = i.fa_start_date if i.fa_start_date else ""
                    end_date = i.fa_end_date if i.fa_end_date else ""
                elif "spring" :
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
        