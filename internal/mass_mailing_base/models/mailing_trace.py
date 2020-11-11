# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MailingTrace(models.Model):

    _inherit = 'mailing.trace'

    trace_type = fields.Selection(selection_add=[('whatsapp', 'Whatsapp')])

    def set_opened(self, mail_mail_ids=None, mail_message_ids=None):

        traces = super(MailingTrace, self).set_opened(mail_mail_ids, mail_message_ids)

        mailing_ids = self.env["mailing.mailing"].search([
            ("campaign_id", "=", self.campaign_id.id),
            ("trigger", "=", "message_opened"),
        ])

        if mailing_ids:
            mailing_ids.action_send_mail(self.env[self.model].browse(self.res_id))

        return traces