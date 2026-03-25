# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ActiveFacilityDependWizardMatching(models.TransientModel):
    _inherit = 'active.facility.depend.wizard'

    def archive_department_and_offers(self):
        for department_id in self.department_ids:
            department_id.archive_department_and_offers()
        
    def archive_department_and_unlink_offers(self):
        for department_id in self.department_ids:
            department_id.archive_department_and_unlink_offers()
        
    def unarchive_department_and_offers(self):
        for department_id in self.department_ids:
            department_id.unarchive_department_and_offers()
        
    def unarchive_department_and_unlink_offers(self):
        for department_id in self.department_ids:
            department_id.unarchive_department_and_unlink_offers()
