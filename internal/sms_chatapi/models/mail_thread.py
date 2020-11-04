# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo.addons.mass_mailing_base.tools import helpers

from odoo import models
from odoo.tools import html2plaintext, plaintext2html


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def normalize_whatsapp_number_in_recipients(self, recipients_info, record):
        """ Normalize number for API whatsapp """
        alternative_number = \
            helpers.valid_alternative_9number(recipients_info.get(record.id))

        if alternative_number:
            number = re.sub('[^0-9]', '', recipients_info.get(record.id).get("number"))
            w_number = "+{}".format(number) \
                if number[:2] == "55" else "+55{}".format(number)
            recipients_info.get(record.id).update(sanitized=w_number)
