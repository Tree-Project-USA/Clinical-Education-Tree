from odoo import http
from odoo.http import request
import base64
from odoo.http import request, route
from odoo.tools.mimetypes import guess_mimetype
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
