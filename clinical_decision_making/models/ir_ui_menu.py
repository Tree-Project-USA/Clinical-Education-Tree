# -- coding: utf-8 --
from odoo.osv import expression
from odoo import models, api, tools


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def get_user_roots(self):
        
        remove_menu = []
        if not self.env.user.has_group('base.group_erp_manager'):
            remove_menu = [self.env.ref(xmlid).id for xmlid in 
                [
                    'base.menu_management',
                    'utm.menu_link_tracker_root',
                    'website.menu_website_configuration',
                    'mail.menu_root_discuss',
                    'spreadsheet_dashboard.spreadsheet_dashboard_menu_root',
                ]
            ]
            return super(IrUiMenu, self).get_user_roots().filtered(lambda menu_id: menu_id.id not in remove_menu)
        return super(IrUiMenu, self).get_user_roots()