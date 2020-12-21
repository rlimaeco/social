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
                "direction_type": "input",
            }

            sms_id = request.env['sms.sms'].sudo().create(params_sms_id)
            message = sms_id.find_and_attach_to_lead()
            if message:
                response = '200 OK - Odoo SUNNIT recebeu SMS do SmsDev'
        else:
            response = 'ERRO - durante a comunicação com o Odoo SUNNIT'
        return str(response)

    @route(['/smsdev/changestate'], type='json', auth="none", methods=['GET', 'POST', 'OPTIONS'], cors="*", csrf=False)
    def smsdev_change_state(self,  **post):
        """
        Webhoock para Atualizar status mensagens do SmsDev
        https://painel.smsdev.com.br/integracao/callback
        POST from smsdev:
        {

            "key": "XXXXXXXXXXXXXXX", // Chave Key usuário
            "id": "123456789",       // ID da mensagem da situação
            "refer": "XXXXXXX",  // Referencia utiliza na mensagem de enviada
            "situacao": "RECEBIDA", // Situação da mensagem
            "data_envio" : "28022020145322", // Formato ddmmrrrrhh24miss
            "operadora": "VIVO-PORTABILIDADE", // Operadora identificada (HLR)
            "qtd_credito": "1" // Qtd de crédito consumido
        }
        """
        post = request.jsonrequest

        if post:
            message_sid = post.get('id')
            message_status = post.get('situacao')

            if message_sid and message_status:
                sms_sms_model = request.env['sms.sms'].sudo()
                sms_id = sms_sms_model.search([
                    ("message_id", "=", message_sid)])
                if sms_id:
                    trace_id = request.env['mailing.trace'].sudo().search([
                        ('sms_sms_id_int', '=', sms_id.id)
                    ])

                    if trace_id:
                        # RECEBIDA – Mensagem entregue no aparelho do cliente
                        # ENVIADA – Mensagem enviada a operadora.
                        if message_status in ["ENVIADA", "RECEBIDA"]:
                            sms_id.set_sent()
