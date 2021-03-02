# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def get_iap(self, sms_id=False):
        """ Buscar o IAP correto"""
        account = self.env["iap.account"]

        account_id = \
            account.search([("name", "=", sms_id.message_type)], limit=1) \
                if sms_id else account.search([], limit=1)

        return account_id

    @api.model
    def _send_sms(self, number, message, sms_id=False):
        """
        Sobrescrita de método para acionar API
        """
        account_id = self.get_iap(sms_id)
        if account_id and account_id.provider != "odoo":
            return self._send_sms_api(account_id, number, message, sms_id)
        else:
            return super()._send_sms(number, message)

    def _send_sms_api(self, account_id, number, message, sms_id=False):
        """Main method to send sms in specific account"""
        raise NotImplementedError()

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

        :return: return of /iap/sms/1/send controller which is a list of dict
         [{
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
