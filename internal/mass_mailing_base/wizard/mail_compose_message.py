# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    scheduled_date = fields.Char(
        string='Scheduled Send Date',
        help="If set, the queue manager will send the email after the date."
             " If not set, the email will be send as soon as possible.",
    )

    def get_mail_values(self, res_ids):
        """ Override method that inject scheduled_date in mail.mail """
        self.ensure_one()
        res = super(MailComposeMessage, self).get_mail_values(res_ids)

        if self.scheduled_date:
            for res_id in res:
                mail_values = res[res_id]
                mail_values.update(scheduled_date=self.scheduled_date)

        return res
