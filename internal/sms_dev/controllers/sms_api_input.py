# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mass_mailing_base.tools import helpers

from odoo import http
from odoo.http import request, route


class SmsDEVWebhooks(http.Controller):

    @route(['/smsdev/input'], type='json', auth="none", methods=['GET', 'POST', 'OPTIONS'], cors="*", csrf=False)
    def smsdev_input(self,  **post):
        """
        Webhoock para receber mensagens do SmsDev
        https://painel.smsdev.com.br/integracao/callback
        POST from smsdev:
        {
            "from": "5562988887777", // Número que enviou o retorno
            "id": "123456789",       // ID do retorno
            "id_sent": "637849052",  // ID da mensagem enviada
            "message": "Teste de retorno", // Mensagem do retorno
            "refer": "XXXXXXX" // Referencia utiliza na mensagem de enviada
        }
        """
        response = "Mensagem recebida"
        post = request.jsonrequest

        if post.get('message', False) and post.get('from', False):

            params_sms_id = {
                "body":  post.get('message'),
                "number": helpers.sanitize_mobile(post.get('from')),
                "message_type": "sms",
                "message_id": post.get("id"),
                "state": "received",
                "type": "input",
            }

            sms_id = request.env['sms.sms'].sudo().create(params_sms_id)
            message = sms_id.find_and_attach_to_lead()
            if message:
                response = '200 OK - Odoo SUNNIT recebeu SMS do SmsDev'
        else:
            response = 'ERRO - durante a comunicação com o Odoo SUNNIT'
        return str(response)
