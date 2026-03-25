# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class StudentCampus(models.Model):
    _name = 'student.campus'
    _description = _('Student Campus')

    name = fields.Char(_('Name'))
    company_id = fields.Many2one('res.company', string='University', default=lambda self: self.env.user.company_id)