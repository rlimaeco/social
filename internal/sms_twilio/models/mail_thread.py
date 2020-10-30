# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
from odoo.addons.phone_validation.tools import phone_validation

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def valid_alternative_9number(self, info):
        """Validar um numero alternativo"""
        if not info.get("number", False):
            return False

        simple_number =  re.sub('[^0-9]', '', info.get("number"))

        # 92415585
        if len(simple_number) == 8:
            alternative_number = "+9{}".format(simple_number)

        # 9 92415585
        if len(simple_number) == 9:
            alternative_number = "+{}".format(simple_number)

        # 35 9241 5585
        elif len(simple_number) == 10:
            alternative_number = "+55{}9{}".format(simple_number[:2], simple_number[-8:])

        # 35 9 9241 5585
        elif len(simple_number) == 11:
            alternative_number = "+55{}".format(simple_number)

        # 55 35 9241 5585
        elif len(simple_number) == 12:
            alternative_number = "+{}9{}".format(simple_number[:4], simple_number[-8:])

        # 55 35 9 9241 5585
        elif len(simple_number) == 13:
            alternative_number = "+{}".format(simple_number)

        else:
            alternative_number = simple_number

        valid_number = phone_validation.phone_sanitize_numbers_w_record(
            [alternative_number], info.get("partner"))

        if valid_number.get(alternative_number).get("sanitized"):
            return valid_number.get(alternative_number).get("sanitized")
        return False

    def _sms_get_recipients_info(self, force_field=False, message_type="sms"):
        """" Manipular numeros de destinatario"""
        recipients_info = \
            super(MailThread, self)._sms_get_recipients_info(force_field)

        for partner in self:
            info = recipients_info.get(partner.id)

            # Para SMS sempre Adicionar o número 9
            if message_type == "sms":
                s_number = self.valid_alternative_9number(info)
                if s_number:
                    recipients_info.get(partner.id).update(sanitized=s_number)
                    return recipients_info

            # Para whatsapp remover espaços em branco
            if message_type == "whatsapp":
                valid_number = self.valid_alternative_9number(info)
                if valid_number:
                    number = re.sub('[^0-9]', '', info.get("sanitized"))

                    w_number = "+{}".format(number) \
                        if number[:2] == "55" else "+55{}".format(number)

                    recipients_info.get(partner.id).update(sanitized=w_number)
                    return recipients_info

        return recipients_info
