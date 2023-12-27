import logging
import werkzeug
from werkzeug.urls import url_encode
from odoo import http, _
from odoo.http import request
import base64
from odoo.tools.mimetypes import guess_mimetype
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Dow(http.Controller):

    @http.route('/contract/attachment/<int:remote_id>', type='http', auth='public')
    def download_attachment(self, remote_id, **kwargs):

        contract_id = request.env['site'].sudo().search([('id', '=', int(remote_id))], limit=1)
        attachment = contract_id.contract_attachment
        content_base64 = base64.b64decode(attachment)
        mimetype = guess_mimetype(base64.b64decode(attachment))
        extension = str(mimetype).split("/")[1]
        httpheaders = [
            ("Content-Type", mimetype),
            ("Content-Length", len(content_base64)),
            (
                "Content-Disposition",
                f'attachment; filename="{contract_id.name}.{extension}"',
            ),
        ]
        return request.make_response(content_base64, headers=httpheaders)
    
    
class CustomAuthSignupHome(AuthSignupHome):
    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('clinical_decision_making.mail_template_send_account_confirmation')
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search([('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
        # result = super(CustomAuthSignupHome, self).web_auth_signup()
        # if 'error' not in  result.qcontext and request.httprequest.method == 'POST':
        #     print(result.qcontext)
        #     User = request.env['res.users']
        #     user_sudo = User.sudo().search(
        #         User._get_login_domain(result.qcontext.get('login')), order=User._get_login_order(), limit=1
        #     )
        #     template = request.env.ref('clinical_decision_making.mail_template_send_account_confirmation', raise_if_not_found=False)
        #     if user_sudo and template:
        #         template.sudo().send_mail(user_sudo.id, force_send=True)
        # return result