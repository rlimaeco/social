# -*- coding: utf-8 -*-
import re
import werkzeug
from twilio.twiml.messaging_response import MessagingResponse

from odoo import http
from odoo.http import request, route


class TwilioWebhooks(http.Controller):

    @route(['/twilio/input'], type='http', auth="none", methods=['GET', 'POST', 'OPTIONS'], cors="*", csrf=False)
    def tw_input(self,  **post):
        """
        Webhoock para receber mensagens do whatsapp sandbox
        https://www.twilio.com/console/sms/whatsapp/sandbox
        """
        res_partner_model = request.env['res.partner'].sudo()
        message_response_twilio = MessagingResponse()
        message = False

        def sanitize_mobile(number):
            """Remover caracteres de controle"""
            return re.sub('[^0-9]', '', sms_from_number)[-8:] if number else ""

        def create_mail_message(partner, body, message_type):
            """Criar mail message para o partner"""
            if partner:
                mail_message_model = request.env['mail.message'].sudo()
                message = mail_message_model.create({
                    'subject': 'Message from Whatsapp',
                    'body': body,
                    'author_id': partner.id,
                    'res_id': partner.id,
                    'email_from': partner.email or False,
                    'model': 'res.partner',
                    'message_type': message_type,
                })
                return message or False

        if post.get('Body', False) and post.get('From', False):
            sms_from_number = post.get('From')
            mobile = sanitize_mobile(sms_from_number)

            # Mensagem de whatsapp atribuir ao partner
            if 'whatsapp' in sms_from_number:
                all_partner_ids = \
                    res_partner_model.search([("mobile", "!=", False)])
                partner_id = all_partner_ids.filtered(
                    lambda x: sanitize_mobile(x.mobile) == mobile )

                if partner_id:
                    message = create_mail_message(
                        partner_id, post.get('Body'), 'whatsapp')

        if message:
            response = '200 OK - Odoo SUNNIT recebeu SMS'
        else:
            response = 'ERRO - durante a comunicação com o Odoo SUNNIT'

        return str(message_response_twilio.message(response))
