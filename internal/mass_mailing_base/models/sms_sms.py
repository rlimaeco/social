# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    message_type = fields.Selection(
        selection=[
            ('sms', 'SMS Phone'),
            ('whatsapp', 'WhatsApp'),
        ],
        string="Message Type",
        compute="compute_message_type",
    )

    @api.depends("mail_message_id")
    def compute_message_type(self):
        for record in self:
            record.message_type = record.mail_message_id.message_type
