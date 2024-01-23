# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AttachmentRequest(models.Model):
    _name = 'attachment.request'
    _description = _('Attachment Request')
    _rec_name = 'student_id'

    student_id = fields.Many2one(comodel_name='res.partner', string='Student Name', domain=[('is_student', '=', True)], tracking=True, required=True)
    medical_attachment_ids = fields.Many2many(
        comodel_name='attachments',
        string="Attachments",
        tracking=True
    )
    note = fields.Text('Internal Notes', tracking=True)
    state = fields.Selection(
        selection=[
            ('under_review', 'Under Review'),
            ('update_required', 'Update Required'),
            ('confirmed', 'Confirmed'),
            ('cancel', 'Cancelled')
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='under_review',
    )
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.user.company_id)
    
    def confirm_attachment(self):
        self.write({
            'state': 'confirmed'
        })
        self.medical_attachment_ids.write({
            'student_id': self.student_id.id
        })
        
    def action_cancel(self):
        self.write({
            'state': 'cancel'
        })
        self.medical_attachment_ids.write({
            'student_id': False,
            })
    
    def action_under_review(self):
        self.write({
            'state': 'under_review'
        })
        self.medical_attachment_ids.write({
            'student_id': False,
            })
        
    def action_update_required(self):
        self.write({
            'state': 'update_required'
        })
        self.medical_attachment_ids.write({
            'student_id': False,
            })

    
    
