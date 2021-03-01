# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mass_mailing_base.tools import helpers
from twilio.twiml.messaging_response import MessagingResponse

from odoo import http
from odoo.http import request, route


class TwilioWebhooks(http.Controller):

    @route(['/twilio/input'], type='http', auth="none", methods=['GET', 'POST', 'OPTIONS'], cors="*", csrf=False)
    def twilio_input_message(self,  **post):
        """
        Webhoock para receber mensagens do whatsapp sandbox
        https://www.twilio.com/console/sms/whatsapp/sandbox
        POST from Twilio:
        {
        'SmsMessageSid': 'SMe8f1366da573cdc95485b7d1143ff1ef',
        'NumMedia': '0',
        'SmsSid': 'SMe8f1366da573cdc95485b7d1143ff1ef',
        'SmsStatus': 'received',
        'Body': 'Corpo da mensagem',
        'To': 'whatsapp:+14155238886',
        'NumSegments': '1',
        'MessageSid': 'SMe8f1366da573cdc95485b7d1143ff1ef',
        'AccountSid': 'ACbd29253caeb9ab0eaa083f4375085d9b',
        'From': 'whatsapp:+556182991273',
        'ApiVersion': '2010-04-01'
        }
        """
        if post.get('Body', False) and post.get('From', False):
            message_type = "sms"
            if "whatsapp" in post.get('From'):
                message_type = "whatsapp"

            params_sms_id = {
                "body":  post.get('Body'),
                "number": helpers.sanitize_mobile(post.get('From')),
                "message_type": message_type,
                "message_id": post.get("SmsMessageSid"),
                "state": "received",
                "direction_type": "input",
            }

            sms_id = request.env['sms.sms'].sudo().create(params_sms_id)
            message = sms_id.find_and_attach_to_lead()
            if message:
                response = '200 OK - Odoo SUNNIT recebeu SMS do Twilio'
        else:
            response = 'ERRO - durante a comunicação com o Odoo SUNNIT'

        message_response_twilio = MessagingResponse()
        return str(message_response_twilio.message(response))

    @route('/twilio/MessageStatus',  type="http", auth="none", methods=['POST','OPTIONS'], cors="*", csrf=False)
    def twilio_incoming_sms_status(self,  **post):
        """ Status de mensagens via twilio """
        if post:
            message_sid = post.get('MessageSid')
            message_status = post.get('MessageStatus')
            if message_sid and message_status:
                sms_sms_model = request.env['sms.sms'].sudo()
                sms_id = sms_sms_model.search([
                    ("message_id", "=", message_sid)])
                if sms_id:
                    # https://www.twilio.com/docs/sms/api/message-resource#message-status-values
                    if message_status in ["sent", "read"]:
                        sms_id.state = "sent"

                    if message_status in ["failed", "undelivered"]:
                        sms_id.state = "error"

                    if message_status in ["received"]:
                        sms_id.state = "received"

                    # State do mailing.trace que garante que whatsapp foi lido
                    if message_status == "read":
                        sms_id.set_opened()

        response = MessagingResponse()
        response.message('Odoo SUNNIT Atualizou status')
        return str(response)
