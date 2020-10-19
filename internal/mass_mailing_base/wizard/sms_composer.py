# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SendSMS(models.TransientModel):
    _inherit = 'sms.composer'

    message_type = fields.Selection(
        selection=[
            ('whatsapp', 'WhatsApp'),
            ('phone-sms', 'SMS'),
        ],
        string='Type',
    )
