# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# Copyright (C) 2021 - Rafael Tatu Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mass_mailing_base.tools import helpers

from odoo import http
from odoo.http import request, route


class ChatAPIWebhooks(http.Controller):

    def change_state_message(self, acks):
        """ Alterar status de Mensagens do CHATAPI """
        responses = []
        for ack in acks:
            sms_id = request.env['sms.sms'].sudo().search([
                ("message_id", "=", ack.get("id"))
            ])

            if sms_id:
                message_status = ack.get("status")
                # State do SMS de enviado ou erro
                if message_status in ["delivered", "viewed"]:
                    sms_id.set_sent()

                # State do mailing.trace que garante que whatsapp foi lido
                if message_status == "viewed":
                    sms_id.set_opened()

            responses.append("Atualizado status do SMS: {}".format(sms_id))
        return responses

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
                    sms_id.set_sent()

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
                    "direction_type": "input",
                }
                sms_id = request.env['sms.sms'].sudo().create(params_sms_id)
                message_id = sms_id.find_and_attach_to_lead()

                if message_id:
                    response = " {}: 200 OK - SUCESSO".format(message.get("id"))
                    responses.append(response)

            else:
                responses.append(" {}: ERRO - Mensagem não processada".
                                format(message.get("id")))

        return responses

    @route(['/chatapi'], type='json', auth="none", methods=['GET', 'POST', 'OPTIONS'], cors="*", csrf=False)
    def chatapi_input(self,  **post):
        """
        Webhoock principal do ChatAPI
         Acessar: https://app.chat-api.com/
         setar: https://odoo.dev.sunnit.com.br/chatapi
        """
        post = request.jsonrequest
        print(post)

        # Mensagem nova
        if post.get('messages'):
            responses = self.inputMessage(post.get('messages'))

        # Alteração de status
        if post.get("ack"):
            responses = self.change_state_message(post.get("ack"))

        response = str(" - ".join(responses))
        return response
