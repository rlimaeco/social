# -*- coding: utf-8 -*-
import re
import werkzeug
from twilio.twiml.messaging_response import MessagingResponse

from odoo import http
from odoo.http import request, route

# https://www.twilio.com/docs/sms/api/message-resource#message-status-values
sms_state = {
    "queued":"outgoing",
    "accepted":"outgoing",
    "sent":"sent",
    "delivered":"sent",
    "received":"sent",
    "read":"read",
    "failed":"error",
    "undelivered":"canceled",
}

class TwilioWebhooks(http.Controller):

    @route(['/twilio/input'], type='http', auth="none", methods=['GET', 'POST', 'OPTIONS'], cors="*", csrf=False)
    def tw_input(self,  **post):
        """
        Webhoock para receber mensagens do whatsapp sandbox
        https://www.twilio.com/console/sms/whatsapp/sandbox
        """
        res_partner_model = request.env['res.partner'].sudo()
        crm_lead_model = request.env['crm.lead'].sudo()

        message_response_twilio = MessagingResponse()
        message = False

        def sanitize_mobile(number):
            """Remover caracteres de controle"""
            return re.sub('[^0-9]', '', sms_from_number)[-8:] if number else ""

        def create_mail_message(model, body, message_type="sms", sms_id=False):
            """Criar mail message para o partner"""
            if partner:
                mail_message_model = request.env['mail.message'].sudo()
                message = mail_message_model.create({
                    'subject': 'Message from Whatsapp',
                    'body': body,
                    'author_id': partner.id,
                    'res_id': model.id,
                    'email_from': partner.email or False,
                    'model': model._name,
                    'message_type': message_type,
                    "message_id": sms_id,
                })
                return message or False

        def get_record_from_number(model, number):
            """Buscar uma lead existente baseado no numero"""
            all_records_ids = model.sudo().search([("mobile", "!=", False)])
            record_id = all_records_ids.filtered(
                lambda x: sanitize_mobile(x.mobile) == number)
            return record_id

        if post.get('Body', False) and post.get('From', False):
            sms_from_number = post.get('From')
            mobile = sanitize_mobile(sms_from_number)

            # Mensagem de whatsapp atribuir ao partner
            if 'whatsapp' in sms_from_number:
                lead_id = get_record_from_number(mobile)

                # Se já existe uma lead, adiciona SMS na thread de comunicação
                if lead_id:
                    message = create_mail_message(
                        lead_id, post.get('Body'),
                        'whatsapp', post.get("SmsSid"))

                # Senão Gerar lead SE encontrar partner
                else:
                    partner_id = get_record_from_number(mobile)
                    if partner_id:
                        lead_id = crm_lead_model.create({
                            "name": "LEAD FROM WHATSAPP",
                            "partner_id": partner_id.id,
                        })

                        message = create_mail_message(
                            partner_id, post.get('Body'),
                            'whatsapp', post.get("SmsSid"))

                    # Senão gerar lead sem partner mas com numero setado
                    else:
                        lead_id = crm_lead_model.create({
                            "name": "LEAD FROM WHATSAPP",
                            "mobile": mobile
                        })
                        message = create_mail_message(
                            lead_id, post.get('Body'),
                            'whatsapp', post.get("SmsSid"))
        if message:
            response = '200 OK - Odoo SUNNIT recebeu SMS'
        else:
            response = 'ERRO - durante a comunicação com o Odoo SUNNIT'

        return str(message_response_twilio.message(response))

    @route('/twilio/MessageStatus',  type="http", auth="none", methods=['POST', 'OPTIONS'], cors="*", csrf=False)
    def incoming_sms_status(self,  **post):
        """
        Status de mensagens via twilio
        """
        if post:
            message_sid = post.get('MessageSid')
            message_status = post.get('MessageStatus')
            if message_sid and message_status:
                sms_sms_model = request.env['sms.sms'].sudo()
                sms_id = sms_sms_model.search([
                    ("message_id", "=", message_sid)])
                if sms_id:
                    sms_id.state = sms_state.get(message_status)
