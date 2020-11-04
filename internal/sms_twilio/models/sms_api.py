# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from werkzeug import urls

from odoo.addons.mass_mailing_base.tools import helpers


from odoo import models
from odoo.exceptions import UserError


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _prepare_twilio_params(self, account, number, message, sms_id):
        """
        Método para preparar dados que irao para API
        """
        return {
            "account_sid": account.twilio_account_sid,
            "auth_token": account.twilio_auth_token,
            "from": self.sanitize_phone_number(
                account.twilio_from_phone, sms_id.message_type),
            "to": self.sanitize_phone_number(number, sms_id.message_type),
            "message": message,
        }

    def add_caracteres_controle(self, number):
        # ADicionar caracteres de controle para twilio
        # Validar código do pais
        code_brazil = "55"
        if number[:2] != code_brazil:
            number = "{}{}".format(code_brazil, number)

        if "+" not in number:
            number = "+{}".format(number)

        return number

    def sanitize_phone_number(self, phone_number, message_type="sms"):
        """
        Sanitizar numero de acordo com tipo de mensagem
        """
        number = self.add_caracteres_controle(phone_number)

        if message_type == "whatsapp":
            return "{}:{}".format(message_type, number)

        elif message_type == "sms":
            return "{}".format(number)

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

            return {"sid": res.sid, "state": res.status}

        except TwilioRestException as e:
            raise UserError(e.msg)
