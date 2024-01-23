from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError

class SubmitAvailability(http.Controller):
    @http.route('/submit/availability/<int:id>', website=True, type='http', auth="user")
    def submitavailability(self, id=None, **kw):
        values = {}
        partner_id = request.env.user.partner_id
        if request.httprequest.method == "GET":
            facility_id = request.env["medical.facility"].sudo().search([("id", "=", id)])
            values["partner_id"] = partner_id 
            values["facility_id"] = facility_id 
            return request.render("website_base.availability_template", values)
        elif request.httprequest.method == "POST":
            department_list = []
            for department in range(0, int(kw.get("len_department"))):
                line_ids= (0,0,{
                    'department_id': kw.get("department_id_" + str(department)),
                    'placement_type': kw.get("placement_type_" + str(department)),
                    'placement_term': kw.get("placement_term_" + str(department)),
                    'year': kw.get("term_" + str(department)),
                    'setting': kw.get("setting_" + str(department)),
                    'offers': kw.get("offers_" + str(department)),
                })
                department_list.append(line_ids)
            vals = {
                "facility_id": kw.get("facility_id") if kw.get("facility_id") else False,
                "line_ids": department_list,
            }
            request.env["placement.offer"].sudo().create(vals)
            return request.render("website_base.success_placement_offer_template")
        
    @http.route('/facility/placement/offer/<int:id>', website=True, type='http', auth="user")
    def facility_placement_offer(self, id=None, **kw):
        partner_id = request.env.user.partner_id
        if request.httprequest.method == "GET":
            facility_id = request.env["medical.facility"].sudo().search([("id", "=", id)])
            archive_ids = request.env['archive'].sudo().search([
                ('facility_id', '=', facility_id.id), 
                ('placement_status', '=', 'pending')
            ])
            values = {
                "department_ids": facility_id.mapped("department_ids").filtered(lambda q: partner_id.id in q.scce_ids.mapped('scce_id').ids),
                "scce_ids": facility_id.mapped("scce_ids"),
                "partner_id": partner_id ,
                "facility_id": facility_id ,
                "archive_ids": archive_ids,
            }
            values.update(dict(request.params))
            dict(request.params)
            request.session['facility_id'] =  facility_id.id
            return request.render("website_base.show_placement_offer_facility_template", values)
        
    @http.route('/assigned/student/<int:id>', website=True, type='http', auth="user")
    def assigned_student(self, id=None, **kw):
        values = {}
        facility_id = request.session.get('facility_id', False)
        archive_id = request.env['archive'].sudo().search([
            ('id', '=', id),
        ])
        for student in archive_id.mapped("student_id"):
            comp_tce1 = request.env['archive'].search_count([('student_id', '=', student.id), ('placement_type', '=', 'tce1'), ('placement_status', 'in', ['completed', 'confirmed'])])
            if comp_tce1:
                pass
            else:
                error = _("Student %s should take TCE 1 term before TCE 2" % (student.name))
                if error:
                    values["error"] = error
                    return request.redirect_query("/facility/placement/offer/%s" % facility_id, values)
        archive_id.sudo().write({
            "placement_status": "confirmed"
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
            "placement_status": "not_placed"
        })

        return request.redirect_query(
                            "/facility/placement/offer/%s" % facility_id)
    @http.route('/cancel/eassigned/student/<int:id>', website=True, type='http', auth="user")
    def cancel_assigned_student(self, id=None, **kw):
        facility_id = request.session.get('facility_id', False)
        archive_id = request.env['archive'].sudo().search([
            ('id', '=', id),
        ])
        archive_id.sudo().write({
            "placement_status": "not_placed"
        })
        archive_id.archive_offer_id.write({
            "active": False,
        })
        return request.redirect_query(
                            "/facility/placement/offer/%s" % facility_id)
        
    @http.route('/profile/student/<int:id>', website=True, type='http', auth="user")
    def profile_student(self, id=None, facility_id=None, **kw):
        values = {}
        student_id = request.env["res.partner"].sudo().search([("id", "=", id)])
        values["student_id"] = student_id
        values["facility_id"] = request.session.get('facility_id', False)
        return request.render("website_base.student_profile_templates", values)
    
    @http.route('/departments', website=True, type='json', auth="user", csrf=False)
    def departments(self, id=None, **kw):
        values = {}
        partner_id = request.env.user.partner_id
        facility_id = request.env["medical.facility"].sudo().search([("id", "=", id)])
        company_id = request.env["res.company"].sudo().search([], limit=1)
        # SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]
        SELECTION_YEAR_RANGE = [{
                    'id': str(i),
                } for i in range(2020, 2500)]
        departments = [{
                    'id': department.id,
                    'name': department.name
                } for department in facility_id.mapped("department_ids")]
        companys = [{
                    'id': company.id,
                    'name': company.name
                } for company in company_id]
        values["partner_id"] = partner_id
        values["facility_id"] = facility_id
        values["company_id"] = companys
        values["department_ids"] = departments
        values["SELECTION_YEAR_RANGE"] = SELECTION_YEAR_RANGE
        return values