# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.mass_mailing_base.tools import helpers
from twilio.twiml.messaging_response import MessagingResponse

from odoo import http, fields
from odoo.http import request, route

_logger = logging.getLogger(__name__)

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
trace_sms_state = {
    "queued":"scheduled",
    "accepted":"scheduled",
    "sent":"sent",
    "delivered":"sent",
    "received":"sent",
    "read":"opened",
    "failed":"bounced",
    "undelivered":"exception",
}


class TwilioWebhooks(http.Controller):

    @route(['/twilio/input'], type='http', auth="none", methods=['GET', 'POST', 'OPTIONS'], cors="*", csrf=False)
    def tw_input(self,  **post):
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
                "type": "input",
            }

            sms_id = request.env['sms.sms'].sudo().create(params_sms_id)
            message = sms_id.find_and_attach_to_lead()
            if message:
                sms_id.set_reply_mailing_trace()
                response = '200 OK - Odoo SUNNIT recebeu SMS do Twilio'
        else:
            response = 'ERRO - durante a comunicação com o Odoo SUNNIT'

        message_response_twilio = MessagingResponse()
        return str(message_response_twilio.message(response))

    @route('/twilio/MessageStatus',  type="http", auth="none", methods=['POST', 'OPTIONS'], cors="*", csrf=False)
    def incoming_sms_status(self,  **post):
        """ Status de mensagens via twilio """
        if post:
            message_sid = post.get('MessageSid')
            message_status = post.get('MessageStatus')
            if message_sid and message_status:
                sms_sms_model = request.env['sms.sms'].sudo()
                sms_id = sms_sms_model.search([
                    ("message_id", "=", message_sid)])
                if sms_id:
                    trace = request.env['mailing.trace'].sudo().search([
                        ('sms_sms_id_int', '=', sms_id.id)
                    ])

                    trace_state = trace_sms_state.get(message_status)
                    if trace and trace_state:
                        trace.write({trace_state: fields.Datetime.now(), 'exception': False})
                        _logger.info(f"TRACE MSG-SID: [{message_sid}] "
                                      f"Alterou Estado para: ['{message_status} ' <-> '{trace_state}' ]")
                    elif trace:
                        trace.set_failed(failure_type=sms_id.IAP_TO_SMS_STATE[trace_state])
                        _logger.error(f"Mensagem SID: [{message_sid}] "
                                      f"com falha: {sms_id.IAP_TO_SMS_STATE[trace_state]}")

                    old_state = sms_id.state
                    new_state = sms_state.get(message_status)
                    sms_id.state = new_state
                    _logger.info(f"SMS: [{message_sid}] "
                                 f"Alteração de Estado: {old_state} -> {new_state}")
                elif message_status == 'failed':
                    _logger.error(f"Não foi possível criar a mensagem (sms.sms),"
                                  f" Erro = {post.get('ErrorMessage')}")

        response = MessagingResponse()
        response.message('Odoo SUNNIT recebeu a mensagem')
        return str(response)
