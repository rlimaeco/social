# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

class MailMessage(models.Model):
    """ Override MailMessage class in order to add a new type: SMS messages.
    Those messages comes with their own notification method, using SMS
    gateway. """
    _inherit = 'mail.message'

    message_id = fields.Char(string="SMS ID")

    message_type = fields.Selection(
        selection_add=[('whatsapp', 'WhatsApp')],
        ondelete={'whatsapp':
                      lambda recs: recs.write({'message_type': 'email'})}
    )
