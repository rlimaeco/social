# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mass_mailing_base.tools import helpers
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from werkzeug import urls

from odoo import models
from odoo.exceptions import UserError


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _prepare_twilio_params(self, account, number, message, sms_id):
        """
        Método para preparar dados que irao para API
        """
        
        if sms_id.message_type == "sms":
            number = helpers.get_number_e164(number)
        
        return {
            "account_sid": account.twilio_account_sid,
            "auth_token": account.twilio_auth_token,
            "from": self.sanitize_phone_number(
                account.twilio_from_phone, sms_id.message_type, add_controls=False),
            "to": self.sanitize_phone_number(number, sms_id.message_type, add_controls=True),
            "message": message,
        }

    def add_caracteres_controle(self, number):
        # ADicionar caracteres de controle para twilio
        # Validar código do pais
        number = helpers.sanitize_mobile_full(number)

        code_brazil = "55"
        if number[:2] != code_brazil:
            number = "{}{}".format(code_brazil, number)

        number = "+{}".format(number)

        return number

    def sanitize_phone_number(self, phone_number, message_type="sms", add_controls=False):
        """
        Sanitizar numero de acordo com tipo de mensagem
        """
        if add_controls:
            phone_number = self.add_caracteres_controle(phone_number)

        if message_type == "whatsapp":
            return "{}:{}".format(message_type, phone_number)

        elif message_type == "sms":
            return "{}".format(phone_number)

        return phone_number

    def _send_sms_api(self, account, number, message, sms_id):
        """Método principal de envio de dados pela API do twilio"""
        if account.provider != "twilio":
            return super(SmsApi, self)._send_sms_api(
                account, number, message, sms_id)

        params = self._prepare_twilio_params(account, number, message, sms_id)

        try:
            base_url = self.env['ir.config_parameter'].sudo().\
                get_param('web.base.url')
            status_callback = urls.url_join(base_url, '/twilio/MessageStatus')
            
            client = \
                Client( params.get("account_sid"), params.get("auth_token"))
            res = client.api.account.messages.create(
                to=params.get("to"),
                from_=params.get("from"),
                body=params.get("message"),
                status_callback=status_callback,
            )
            if res:
                sms_id.message_id = res.sid

                if res.error_code:
                    sms_id.error_code = "{} {}".format(
                        res.error_code, res.error_message)

                # Setar sms e trace como enviados.
                if res.status in ["sent", "queued"]:
                    sms_id.set_sent()

            twilio_to_iap = {
                'queued': 'sent',
                'sent': 'sent',
                'undelivered': 'sms_number_format',
                'failed': 'sms_server'
            }

            return {"sid": res.sid, "state": twilio_to_iap.get(res.status, False) or res.status}

        except TwilioRestException as e:
            raise UserError(e.msg)
