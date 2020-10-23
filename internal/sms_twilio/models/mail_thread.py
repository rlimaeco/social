# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
from odoo.addons.phone_validation.tools import phone_validation

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _sms_get_recipients_info(self, force_field=False, message_type="sms"):
        """" Aceitar numeros com 9 a menos
        """
        recipients_info = \
            super(MailThread, self)._sms_get_recipients_info(force_field)

        if not recipients_info.get(self.id).get("sanitized"):
            info = recipients_info.get(self.id)
            alternative_number = "+{}9{}".format(
                re.sub('[^0-9]', '', info.get("number"))[:4],
                re.sub('[^0-9]', '', info.get("number"))[-8:]
            )
            valid_number = phone_validation.phone_sanitize_numbers_w_record(
                [alternative_number], info.get("partner"))

            if valid_number.get(alternative_number).get("sanitized"):

                if message_type == "whatsapp":
                    w_number = \
                        "+{}".format(re.sub('[^0-9]', '', info.get("number")))
                    recipients_info.get(self.id).update(sanitized=w_number)

                elif message_type == "sms" :
                    recipients_info.get(self.id).update(
                        sanitized=alternative_number)

        return recipients_info
