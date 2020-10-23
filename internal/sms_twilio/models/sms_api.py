# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from odoo import api, models
from odoo.exceptions import UserError
from werkzeug import urls

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

    def sanitize_phone_number(self, phone_number, message_type="sms"):
        """
        Sanitizar numero de acordo com tipo de mensagem
        """
        if message_type == "whatsapp":
            return "{}:{}".format(message_type, phone_number)

        elif message_type == "sms":
            return "{}".format(phone_number)

        return phone_number

    def _send_sms_with_twilio(self, account, number, message, sms_id):
        """
        Método princiapl de envio de dados pela API do twilio
        """
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

            return {"sid": res.sid, "state": res.status}

        except TwilioRestException as e:
            raise UserError(e.msg)

    @api.model
    def _send_sms(self, number, message, sms_id=False):
        """
        Sobrescrita de método para acionar o API do twilio
        """
        account = self.env["iap.account"]
        account_id = \
            account.search([("name", "=", sms_id.message_type)], limit=1) \
                if sms_id else account.search([], limit=1)

        if account_id and account_id.provider == "twilio":
            return self._send_sms_with_twilio(
                account_id, number, message, sms_id)
        else:
            return super()._send_sms(number, message)

    @api.model
    def _send_sms_batch(self, messages):
        """ Sobrescrita de metodo para injetar o parametro de message type
        Send SMS using IAP in batch mode

        :param messages: list of SMS to send, structured as dict [{
            'res_id':  integer: ID of sms.sms,
            'number':  string: E164 formatted phone number,
            'content': string: content to send
            'message_type': string: type do sms: sms or whatsapp
        }]

        :return: return of /iap/sms/1/send controller which is a list of dict [{
            'res_id': integer: ID of sms.sms,
            'state':  string: 'insufficient_credit' or
                                'wrong_number_format' or 'success',
            'credit': integer: number of credits spent to send this SMS,
        }]

        :raises: normally none
        """
        for message in messages:
            # workaround para pegar message_type do sms ja instanciado
            sms_id = self.env["sms.sms"].browse(message.get("res_id"))

            message.update(self._send_sms(
                message.get("number"), message.get("content"), sms_id ))

        return messages
