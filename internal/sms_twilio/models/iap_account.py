# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("twilio", "Twilio")],
        ondelete={'twilio': 'set default'},
    )

    twilio_account_sid = fields.Char(
        string="SID",
    )

    twilio_auth_token = fields.Char(
        string="Auth Token",
    )

    twilio_from_phone = fields.Char(
        string="From Phone",
    )

    def _get_service_from_provider(self):
        if self.provider == "twilio":
            return "sms"

    @property
    def _server_env_fields(self):
        """Campos do Twilio"""
        res = super()._server_env_fields
        res.update(
            {
                "twilio_account_sid": {},
                "twilio_auth_token": {},
                "twilio_from_phone": {},
            }
        )
        return res
