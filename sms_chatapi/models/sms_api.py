# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import re

import requests
from odoo.addons.mass_mailing_base.tools import helpers

from odoo import models


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def sanitize_number_SmsApi(self, number):
        """ Tratar numero para envio do CHATAPI """
        alternative_number = helpers.get_number_e164(number)
        w_number = re.sub('[^0-9]', '', alternative_number)
        return w_number

    def _prepare_chatapi_params(self, account, number, message, sms_id):
        """
        Método para preparar dados que irao para API
        """
        return {
            "chatapi_url": account.chatapi_url,
            "chatapi_token": account.chatapi_token,
            "phone": self.sanitize_number_SmsApi(number),
            "body": message,
        }

    def _send_sms_api(self, account, number, message, sms_id):
        """Método principal de envio de dados pela API"""
        if account.provider != "chatapi":
            return super(SmsApi, self)._send_sms_api(
                account, number, message, sms_id)

        params = self._prepare_chatapi_params(account, number, message, sms_id)

        url = "{}sendMessage?token={}".format(
            params.get("chatapi_url"),
            params.get("chatapi_token")
        )

        response = requests.post(url, data=params)

        if response:
            result = json.loads(response.content)
            sms_id.message_id = result.get("id")

            print(response.content)
            return {
                "sid": result.get("id"),
                "state": json.loads(response.content).get("message")
            }
