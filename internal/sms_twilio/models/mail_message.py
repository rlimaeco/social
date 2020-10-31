# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    message_id = fields.Char(
        string="SMS ID",
    )
