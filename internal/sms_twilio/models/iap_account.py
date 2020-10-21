# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("twilio", "Twilio")],
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
