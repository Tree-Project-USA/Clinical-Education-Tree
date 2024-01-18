from odoo import http
from odoo.http import request

class SubmitAvailability(http.Controller):
    @http.route('/submit/availability/<int:id>', website=True, type='http', auth="user")
    def submitavailability(self, id=None, **kw):
        values = {}
        partner_id = request.env.user.partner_id
        if request.httprequest.method == "GET":
            facility_id = request.env["medical.facility"].sudo().search([("id", "=", id)])
            company_id = request.env["res.company"].sudo().search([], limit=1)
            SELECTION_YEAR_RANGE = [(str(i),str(i)) for i in range(2020, 2500)]
            values["partner_id"] = partner_id 
            values["facility_id"] = facility_id 
            values["company_id"] = company_id 
            values["SELECTION_YEAR_RANGE"] = SELECTION_YEAR_RANGE 
            return request.render("website_base.availability_template", values)
        elif request.httprequest.method == "POST":
            vals = {
                "facility_id": kw.get("facility_id") if kw.get("facility_id") else False,
                # "university": kw.get("university") if kw.get("university") else False,
                "placement_term": kw.get("placement_term") if kw.get("placement_term") else False,
                "year": kw.get("term") if kw.get("term") else False,
                "placement_type": kw.get("placement_type") if kw.get("placement_type") else False,
            }
            offer_id = request.env["placement.offer"].sudo().create(vals)
            vals2 = {
                "offer_id": offer_id.id,
                "offers": kw.get("offers") if kw.get("offers") else False,
                "setting": kw.get("setting") if kw.get("setting") else False,
            }
            request.env["placement.offer.line"].sudo().create(vals2)
            return request.render("website_base.success_placement_offer_template")
        
    @http.route('/facility/placement/offer/<int:id>', website=True, type='http', auth="user")
    def facility_placement_offer(self, id=None, **kw):
        values = {}
        partner_id = request.env.user.partner_id
        if request.httprequest.method == "GET":
            facility_id = request.env["medical.facility"].sudo().search([("id", "=", id)])
            archive_offer_ids = request.env['archive'].sudo().search([
                ('facility_id', '=', facility_id.id), 
                ('placement_status', '=', 'pending')
            ]).mapped('archive_offer_id')
            values["partner_id"] = partner_id 
            values["facility_id"] = facility_id 
            values["placement_offer_ids"] = archive_offer_ids
            return request.render("website_base.show_placement_offer_facility_template", values)
        
    @http.route('/assigned/student/<int:id>', website=True, type='http', auth="user")
    def assigned_student(self, id=None, **kw):
        archive_offer_ids = request.env['archive.offer'].sudo().search([
            ('id', '=', id),
        ])
        archive_id = request.env['archive'].sudo().search([
            ('student_id', '=', archive_offer_ids.mapped('student_id').id),
            ('facility_id', '=', archive_offer_ids.mapped('facility_id').id),
        ])
        archive_id.sudo().write({
            "placement_status": "confirmed"
        })
        return request.redirect_query(
                            "/facility/placement/offer/%s" % archive_offer_ids.mapped('facility_id').id)
        
    @http.route('/declin/eassigned/student/<int:id>', website=True, type='http', auth="user")
    def declin_assigned_student(self, id=None, **kw):

        archive_offer_ids = request.env['archive.offer'].sudo().search([
            ('id', '=', id),
        ])
        archive_id = request.env['archive'].sudo().search([
            ('student_id', '=', archive_offer_ids.mapped('student_id').id),
            ('facility_id', '=', archive_offer_ids.mapped('facility_id').id),
        ])
        archive_id.sudo().write({
            "placement_status": "not_placed"
        })
        archive_offer_ids.sudo().write({
            "active": False,
        })
        return request.redirect_query(
                            "/facility/placement/offer/%s" % archive_offer_ids.mapped('facility_id').id)
