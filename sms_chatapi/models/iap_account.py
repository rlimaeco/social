# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("chatapi", "ChatAPI")],
        ondelete={'chatapi': 'set default'},
    )

    chatapi_token = fields.Char(
        string="Auth Token ChatAPI",
    )

    chatapi_url = fields.Char(
        string="Your API URL",
    )
