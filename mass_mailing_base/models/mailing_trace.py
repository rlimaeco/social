# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailingTrace(models.Model):

    _inherit = 'mailing.trace'

    def set_sent(self, mail_mail_ids=None, mail_message_ids=None):
        traces = self._get_records(mail_mail_ids, mail_message_ids, [('sent', '=', False)])
        traces.write({'sent': fields.Datetime.now(), 'bounced': False})
        return traces

    trace_type = fields.Selection(
        selection_add=[('whatsapp', 'Whatsapp')],
    )
