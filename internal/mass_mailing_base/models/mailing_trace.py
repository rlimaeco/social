# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MailingTrace(models.Model):

    _inherit = 'mailing.trace'

    trace_type = fields.Selection(selection_add=[('whatsapp', 'Whatsapp')])
