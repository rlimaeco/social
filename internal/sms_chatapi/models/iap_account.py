# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("chatapi", "ChatAPI")],
    )

    chatapi_token = fields.Char(
        string="Auth Token ChatAPI",
    )

    chatapi_url = fields.Char(
        string="Your API URL",
    )
