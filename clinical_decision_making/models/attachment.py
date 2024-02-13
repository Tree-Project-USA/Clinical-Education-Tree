import base64

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AttachmentType(models.Model):
    _name = "attachment.type"
    _description = "attachment type"
    _rec_name = "name"

    name = fields.Char("Name", required=True)
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)
    portal_id = fields.Char("ID")
    description = fields.Text("Description")
    is_required = fields.Boolean(string="Is Required")


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

