# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("smsdev", "SmsDev")],
    )

    smsdev_type = fields.Char(
        string="Type",
        default="9",
    )

    smsdev_token = fields.Char(
        string="SmsDev Key",
    )
