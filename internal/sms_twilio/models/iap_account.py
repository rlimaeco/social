# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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

    def get_provider_states(self, type):
        """Estados do Twilio para SMS_STATE"""
        # TODO Módulo base pode ter esta função e aqui ser um overwrite dela
        # super(IapAccount, self).get_provider_states(type)
        if self.provider == 'twilio':
            if type in ['sms', 'whatsapp']:
                # No caso do twilio os estados entre sms e whatsapp são os iguais
                return {
                    'queued': 'sent',
                    'sent': 'sent',
                    'undelivered': 'sms_number_format',
                    'failed': 'sms_server'
                }
        else:
            # Odoo IAP_TO_SMS_STATE
            # TODO: retorno padrão do super
            return {
                'success': 'sent',
                'insufficient_credit': 'sms_credit',
                'wrong_number_format': 'sms_number_format',
                'server_error': 'sms_server'
            }


