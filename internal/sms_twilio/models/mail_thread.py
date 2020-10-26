# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
from odoo.addons.phone_validation.tools import phone_validation

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def valid_alternative_9number(self, info):
        """Validar um numero alternativo"""
        alternative_number = "+{}9{}".format(
            re.sub('[^0-9]', '', info.get("number"))[:4],
            re.sub('[^0-9]', '', info.get("number"))[-8:]
        )
        valid_number = phone_validation.phone_sanitize_numbers_w_record(
            [alternative_number], info.get("partner"))

        if valid_number.get(alternative_number).get("sanitized"):
            return valid_number.get(alternative_number).get("sanitized")
        return False

    def _sms_get_recipients_info(self, force_field=False, message_type="sms"):
        """" Manipular numeros de destinatario"""
        recipients_info = \
            super(MailThread, self)._sms_get_recipients_info(force_field)

        info = recipients_info.get(self.id)

        # Para SMS sempre Adicionar o número 9
        if message_type == "sms":
            s_number = self.valid_alternative_9number(info)
            if s_number:
                recipients_info.get(self.id).update(sanitized=s_number)
                return recipients_info

        # Para whatsapp remover espaços em branco
        if message_type == "whatsapp":
            w_number = "+{}".format(re.sub('[^0-9]', '', recipients_info.get(self.id).get("sanitized")))

            valid_number = self.valid_alternative_9number(info)
            if valid_number:
                recipients_info.get(self.id).update(sanitized=w_number)
                return recipients_info

        return recipients_info
