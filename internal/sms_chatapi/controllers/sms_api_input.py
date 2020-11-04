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

        for message in messages:

            # Confirmação de envio
            if message.get("fromMe"):
                sid = message.get("id")

                sms_id = request.env['sms.sms'].sudo().search([
                    ("message_id", "=", sid)
                ])

                if sms_id:
                    sms_id.state = "sent"

            # Mensagem recebida
            elif message.get("body"):
                message_type = "whatsapp"

                params_sms_id = {
                    "body":  message.get('body'),
                    "number":
                        helpers.sanitize_mobile_full(message.get('author')),
                    "message_type": message_type,
                    "message_id": message.get("id"),
                    "state": "received",
                    "type": "input",
                }
                sms_id = request.env['sms.sms'].sudo().create(params_sms_id)
                message_id = sms_id.find_and_attach_to_lead()

                if message_id:
                    responses.append(
                        " {}: 200 OK - MSG processada com SUCESSO".format(
                            message.get("id")))
            else:
                responses.append(" {}: ERRO - Mensagem não processada".
                                format(message.get("id")))

        return responses

    @route(['/chatapi'], type='json', auth="none", methods=['GET', 'POST', 'OPTIONS'], cors="*", csrf=False)
    def chatapi_input(self,  **post):
        """
        Webhoock principal do ChatAPI
        https://app.chat-api.com/
        """
        response = "MENSAGEM RECEBIDA"
        post = request.jsonrequest
        print(post)
        if post.get('messages'):
            responses = self.inputMessage(post.get('messages'))

        response = str(" - ".join(responses))
        return response
