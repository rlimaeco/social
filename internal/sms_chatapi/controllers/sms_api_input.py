# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mass_mailing_base.tools import helpers

from odoo import http
from odoo.http import request, route


class ChatAPIWebhooks(http.Controller):


    def inputMessage(self, messages):
        """
        {
        "id": "false_17472822486@c.us_DF38E6A25B42CC8CCE57EC40F",
        "body": "Ok!",
        "type": "chat",
        "senderName": "Ilya",
        "fromMe": true,
        "author": "17472822486@c.us",
        "time": 1504208593,
        "chatId": "17472822486@c.us",
        "messageNumber": 100
        }
        """
        responses = []
        for post in messages:
            if post.get("body"):
                message_type = "whatsapp"

                params_sms_id = {
                    "body":  post.get('body'),
                    "number": helpers.sanitize_mobile_full(post.get('author')),
                    "message_type": message_type,
                    "message_id": post.get("id"),
                    "state": "received",
                    "type": "input",
                }
                sms_id = request.env['sms.sms'].sudo().create(params_sms_id)
                message = sms_id.find_and_attach_to_lead()

                if message:
                    responses.append(" {}: 200 OK - MSG processada com SUCESSO".
                                format(post.get("id")))
            else:
                responses.append(" {}: ERRO - Mensagem não processada".
                                format(post.get("id")))

        return responses

    @route(['/chatapi'], type='json', auth="none", methods=['GET', 'POST', 'OPTIONS'], cors="*", csrf=False)
    def chatapi_input(self,  **post):
        """
        Webhoock principal do ChatAPI
        https://app.chat-api.com/
        """
        response = "MENSAGEM RECEBIDA"
        post = request.jsonrequest
        if post.get('messages'):
            responses = self.inputMessage(post.get('messages'))

        response = str(" - ".join(responses))
        return response
