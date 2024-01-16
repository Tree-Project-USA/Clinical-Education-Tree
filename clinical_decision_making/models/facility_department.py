# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class FacilityDepartment(models.Model):
    _name = 'facility.department'
    _description = _('FacilityDepartment')

    name = fields.Char(_('Name'))
    facility_id = fields.Many2one(comodel_name='medical.facility', string='Facility')
    geographical_id = fields.Many2one(comodel_name='geographical', string='Zip Code')
    city = fields.Char(related='geographical_id.city')
    state = fields.Char(related='geographical_id.state')
    scce_ids = fields.Many2many(comodel_name='scce.facility', string='SCCE Facility')
    preferred_setting_ids = fields.Many2many(comodel_name='preferred.setting', string='Setting')
    
