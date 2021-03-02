# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

import requests

from odoo import models


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _prepare_smsdev_params(self, account, number, message):
        return {
            "key": account.smsdev_token,
            "type": account.smsdev_type,
            "number": number,
            "msg": message,
        }

    def _send_sms_api(self, account, number, message, sms_id):
        """Método principal de envio de dados pela API SmsDev"""
        if account.provider != "smsdev":
            return super(SmsApi, self)._send_sms_api(
                account, number, message, sms_id)

        params = self._prepare_smsdev_params(account, number, message)

        url = 'https://api.smsdev.com.br/v1/send'
        # Ambiente de homologacao
        if account.smsdev_type == "1":
            url = "http://localhost/smsdev/homolog"

        response = requests.post(url, params=params)

        if response:
            result = json.loads(response.content)
            sms_id.message_id = result.get("id")

            if result.get("situacao") == "OK":
                sms_id.set_sent()

            print(response.content)
            return {
                "sid": result.get("id"),
                "state": result.get("situacao")
            }
