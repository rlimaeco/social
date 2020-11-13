# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class MailingTrace(models.Model):

    _inherit = 'mailing.trace'

    trace_type = fields.Selection(selection_add=[('whatsapp', 'Whatsapp')])

    def get_scheduled(self, mailing_id):
        """   """
        scheduled = fields.Datetime.now() + relativedelta(minutes=1)
        
        if mailing_id.trigger_type_time == "hours":
            scheduled += relativedelta(hours=mailing_id.trigger_qty_time)

        if mailing_id.trigger_type_time == "days":
            scheduled += relativedelta(days=mailing_id.trigger_qty_time)

        return scheduled

    def get_mailing(self, trigger):
        """ Get mailing  off campaign from mailing.trace """

        mailing_id = self.env["mailing.mailing"].search([
            ("campaign_id", "=", self.campaign_id.id),
            ("trigger", "=", trigger),
            # ("trigger_mailing_id", "=", self.mass_mailing_id.id),
            # ("mailing_type", "=", self.trace_type),
        ], limit=1)

        return mailing_id

    def set_opened(self, mail_mail_ids=None, mail_message_ids=None):
        """   """
        traces = super(MailingTrace, self).\
            set_opened(mail_mail_ids, mail_message_ids)

        mailing_id = self.get_mailing("message_opened")

        if mailing_id:
            scheduled = self.get_scheduled(mailing_id)
            res_ids = self.env[self.model].browse(self.res_id).ids
            mailing_id.action_send_mail(res_ids, scheduled_date=scheduled)

        return traces

    def set_replied(self, mail_mail_ids=None, mail_message_ids=None):
        """   """
        traces = super(MailingTrace, self).\
            set_replied(mail_mail_ids, mail_message_ids)

        mailing_id = self.get_mailing("message_replied")

        if mailing_id:
            scheduled = self.get_scheduled(mailing_id)
            res_ids = self.env[self.model].browse(self.res_id).ids
            mailing_id.action_send_mail(res_ids, scheduled_date=scheduled)

        return traces

    def set_opened_test(self):
        """ Função para testar  """
        self.set_opened()
