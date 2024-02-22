import base64

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AttachmentType(models.Model):
    _name = "attachment.type"
    _description = "Program attachment type"
    _rec_name = "name"

    name = fields.Char("Name", required=True)
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)
    portal_id = fields.Char("ID")
    description = fields.Text("Description")
    is_required = fields.Boolean(string="Is Required")
    
    
    @api.model
    def create(self, values):
        # Add code here
        res = super(AttachmentType, self).create(values)
        res.create_student_scce_attachment()
        return res

    def create_student_attachment(self):
        student_ids = self.env["res.partner"].search(
            [("is_student", "=", True), ("company_id", "=", self.company_id.id)])
        for rec in student_ids:
            rec.write({
                "medical_attachment_ids": [(0, 0,
                                                 {
                                                     "company_id": self.company_id.id,
                                                     "attachment_type": self.id

                                                 })]
            })
class ScceAttachmentType(models.Model):
    _name = "scce.attachment.type"
    _description = "Site Attachment Type"
    _rec_name = "name"

    name = fields.Char("Name", required=True)
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)
    portal_id = fields.Char("Portal ID")
    description = fields.Text("Description")
    is_required = fields.Boolean(string="Is Required")
    scce_id = fields.Many2one(comodel_name='res.partner', string='SCCE', domain=[('is_scce', '=', True)], tracking=True, required=True, check_company=True)
 
 
    @api.model
    def create(self, values):
        # Add code here
        res = super(ScceAttachmentType, self).create(values)
        res.create_student_scce_attachment()
        return res

    def create_student_scce_attachment(self):
        student_ids = self.env["res.partner"].search(
            [("is_student", "=", True), ("company_id", "=", self.company_id.id)])
        for rec in student_ids:
            rec.write({
                "scce_medical_attachment_ids": [(0, 0,
                                                 {
                                                     "company_id": self.company_id.id,
                                                     "scce_attachment_type": self.id

                                                 })]
            })
class Attachment(models.Model):
    _name = "attachments"
    _rec_name = "attachment_type"

    student_id = fields.Many2one("res.partner", string="Student", check_company=True)
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)
    request_id = fields.Many2one("attachment.request", string="Request", check_company=True)
    attachment_type = fields.Many2one("attachment.type", string="Attachment Type", check_company=True)
    attachment_ids = fields.Many2many(comodel_name='ir.attachment', string="Attachments", tracking=True, check_company=True)   
    expiration_date = fields.Date(string='Expiration Date')   
    note = fields.Text(string="Note")
    state = fields.Selection([
            ('under_review', 'Under Review'),            
            ('required_update', 'Required Update'),
            ('confirmed', 'Confirmed'),
            ('cancel', 'Cancelled'),
        ], string='Status')
    
    def action_under_review(self):
        self.write(
            {
                'state':  'under_review'
            }
        )
    def action_required_update(self):
        self.write(
            {
                'state':  'required_update'
            }
        )
    def action_confirmed(self):
        self.write(
            {
                'state': 'confirmed' 
            }
        )
    def action_cancel(self):
        self.write(
            {
                'state': 'cancel' 
            }
        )
    
class ScceAttachment(models.Model):
    _name = "scce.attachments"
    _rec_name = "scce_attachment_type"

    student_id = fields.Many2one("res.partner", string="Student", check_company=True)
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)
    request_id = fields.Many2one("scce.attachment.request", string="Request", check_company=True)
    scce_attachment_type = fields.Many2one("scce.attachment.type", string="SCCE Attachment Type", check_company=True)
    attachment_ids = fields.Many2many(comodel_name='ir.attachment', string="Attachments", tracking=True, check_company=True)   
    expiration_date = fields.Date(string='Expiration Date')   
    note = fields.Text(string="Note")
    state = fields.Selection([
            ('under_review', 'Under Review'),            
            ('required_update', 'Required Update'),
            ('confirmed', 'Confirmed'),
            ('cancel', 'Cancelled'),
        ], string='Status')
    
    def action_under_review(self):
        self.write(
            {
                'state':  'under_review'
            }
        )
    def action_required_update(self):
        self.write(
            {
                'state':  'required_update'
            }
        )
    def action_confirmed(self):
        self.write(
            {
                'state': 'confirmed' 
            }
        )
    def action_cancel(self):
        self.write(
            {
                'state': 'cancel' 
            }
        )
