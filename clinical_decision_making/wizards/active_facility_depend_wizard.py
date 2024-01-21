# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ActiveFacilityDependWizard(models.TransientModel):
    _name = 'active.facility.depend.wizard'
    _description = _('Active Facility Depend Wizard')

    facility_id = fields.Many2one(comodel_name='medical.facility', string='Medical Facility')
    department_ids = fields.One2many(comodel_name='facility.department', related='facility_id.department_ids')


    def archive_department(self):
        for department_id in self.department_ids:
            department_id.archive_department()
        
    def archive_department_and_offers(self):
        for department_id in self.department_ids:
            department_id.archive_department_and_offers()
        
    def archive_department_and_unlink_offers(self):
        for department_id in self.department_ids:
            department_id.archive_department_and_unlink_offers()

    def unarchive_department(self):
        for department_id in self.department_ids:
            department_id.unarchive_department()

        
    def unarchive_department_and_offers(self):
        for department_id in self.department_ids:
            department_id.unarchive_department_and_offers()

        
    def unarchive_department_and_unlink_offers(self):
        for department_id in self.department_ids:
            department_id.unarchive_department_and_unlink_offers()
