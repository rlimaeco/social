# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, exceptions, fields, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    message_id = fields.Char(
        string="SMS ID",
    )
