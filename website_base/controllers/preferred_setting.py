import requests
import json
from odoo import _, http
from odoo.http import request, route
from odoo.exceptions import ValidationError
from odoo.tools import lazy
# from odoo.addons.website_sale.controllers.main import 

def split_data_into_groups(data, group_size):
    return [data[i:i+group_size] for i in range(0, len(data), group_size)]

class PreferredSetting(http.Controller):
    
    @http.route("/add/preferred/setting", type="http", website=True, auth="user", Methods=["POST"])
    def add_setting(self, **kw):
        res_partner_id = request.env.user.partner_id
        values = {}

        if request.httprequest.method == "GET":
            setting_ip_ids = request.env["preferred.setting"].search([("type_setting", "=", 'ip')])
            setting_op_ids = request.env["preferred.setting"].search([("type_setting", "=", 'op')])
            preferred_setting_ids = request.env["preferred.setting"].search([])
            values.update({
                'setting_ip_ids' :  setting_ip_ids,
                'setting_op_ids' :   setting_op_ids ,         
                'preferred_setting_ids' : preferred_setting_ids,
                'preferred_list_id' : res_partner_id.preferred_setting_ids.ids or []
           })
            return request.render("website_base.preferred_setting_template", values)
        elif request.httprequest.method == "POST":
                list_setting = [int(x) for x in kw.get('list_setting').split(",")]
                res_partner_id.sudo().write({
                    'preferred_setting_ids' : list_setting
                                             })
                template = request.env.ref('cdm_base.mail_template_send_preferred_settings_added')
                template.sudo().send_mail(request.env.user.id, force_send=True)
                return request.redirect("/my/home")
           
    @http.route(
        ["/check/preferred/setting"], type="json", auth="user", methods=['POST'], website=True, csrf=False
    )
    def check_preferred_setting(self, **post):
        list_type_setting_op = []
        list_type_setting_ip = []
        list_setting = [int(x) for x in post.get('list_setting')]
        preferred_setting_ids = (
            request.env["preferred.setting"].sudo().search([("id", "in", list_setting)])
        )
        for setting_id in preferred_setting_ids:
            if setting_id.type_setting == 'op':
                list_type_setting_op.append(setting_id.id)
            else:
                list_type_setting_ip.append(setting_id.id)
        
        if len(list_type_setting_op) == 5 or len(list_type_setting_ip) == 5:
            return False
        else:
            return True
    
    
