# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import requests
import json

from odoo import models


class SmsApi(models.AbstractModel):
    _inherit = "sms.api"

    def _prepare_smsdev_params(self, account, number, message, sms_id):
        """ pass """
        return {
            "key": account.smsdev_token,
            "type": account.smsdev_type,
            "number": number,
            "msg": message,
        }

    def _send_sms_api(self, account, number, message, sms_id):
        """Método principal de envio de dados pela API SmsDev"""
        if account.provide != "smsdev":
            return super(SmsApi, self)._send_sms_api(
                account, number, message, sms_id)

        params = self._prepare_smsdev_params(account, number, message, sms_id)

        # params = (
        #     ('key',
        #      'ISDX9XT8ZY1KD1P7N8BNIX8TTGQQ4A3AUABPO1D7TGAVNSLYLR00MMJC94NE8XJU9CA233FHOMI6PURF8QQRXNM4EZ4WZW12SKXQW0FADI6CGBRHUE55K6YNCEZ20GKH'),
        #     ('type', '9'),
        #     ('number', params.get("to")),
        #     ('msg', params.get("message")),
        # )

        url = 'https://api.smsdev.com.br/v1/send'
        response = requests.post(url, params=params)

        if response:
            result = json.loads(response.content)
            sms_id.message_id = result.get("id")

            print(response.content)
            return {
                "sid": result.get("id"),
                "state": json.loads(response.content).get("situacao")
            }
