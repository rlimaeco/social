# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailingTrace(models.Model):

    _inherit = 'mailing.trace'

    trace_type = fields.Selection(
        selection_add=[('whatsapp', 'Whatsapp')],
    )
