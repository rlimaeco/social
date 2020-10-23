# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    state = fields.Selection(selection_add=[('read', 'Lido')])

    message_id = fields.Char(
        string="SMS ID",
    )
