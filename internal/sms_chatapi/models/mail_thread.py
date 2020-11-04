# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo.addons.mass_mailing_base.tools import helpers

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def normalize_whatsapp_number_in_recipients(self, recipients_info, record):
        """ Normalize number for API whatsapp """
        alternative_number = \
            helpers.valid_alternative_9number(recipients_info.get(record.id))

        if alternative_number:
            w_number = re.sub('[^0-9]', '', alternative_number)
            recipients_info.get(record.id).update(sanitized=w_number)
