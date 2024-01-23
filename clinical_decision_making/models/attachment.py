import base64

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AttachmentType(models.Model):
    _name = "attachment.type"
    _description = "attachment type"
    _rec_name = "name"

    name = fields.Char("Name", required=True)
    portal_id = fields.Char("ID")
    description = fields.Text("Description")
    is_required = fields.Boolean(string="Is Required")


class Attachment(models.Model):
    _name = "attachments"
    _rec_name = "attachment_type"

    student_id = fields.Many2one("res.partner", string="Student")
    attachment_type = fields.Many2one(
        "attachment.type", string="Attachment Type"
    )
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        string="Attachments",
        tracking=True
    )   
    expiration_date = fields.Date(string='Expiration Date')   
    note = fields.Text(string="Note")

