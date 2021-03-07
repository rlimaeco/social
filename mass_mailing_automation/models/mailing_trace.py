# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from odoo import fields, models
from odoo.addons.mass_mailing_automation.tools import helpers
from odoo.osv.expression import AND, OR


class MailingTrace(models.Model):

    _inherit = 'mailing.trace'

    def get_scheduled(self, mailing_id):
        scheduled = fields.Datetime.now() + relativedelta(hours=-3)
        return helpers.define_time_trigger(mailing_id, scheduled)

    def get_mailing(self, trigger):
        """ Get mailing  off campaign from mailing.trace """
        mailing_id = self.env["mailing.mailing"].search([
            ("campaign_id", "=", self.campaign_id.id),
            ("trigger", "=", trigger),
            ("trigger_mailing_id", "=", self.mass_mailing_id.id),
            ("mailing_type", "=", self.trace_type),
        ], limit=1)

        return mailing_id

    def set_opened(self, mail_mail_ids=None, mail_message_ids=None):
        """   """
        traces = super(MailingTrace, self).\
            set_opened(mail_mail_ids, mail_message_ids)
        status = "message_opened"
        traces.sync_lead(status)
        mailing_id = traces.get_mailing(status)

        if mailing_id:
            scheduled = self.get_scheduled(mailing_id)
            mailing_id.action_send_mail([traces.res_id], scheduled_date=scheduled)

        return traces

    def set_clicked(self, mail_mail_ids=None, mail_message_ids=None):
        """   """
        traces = super(MailingTrace, self).\
            set_clicked(mail_mail_ids, mail_message_ids)
        status = "message_clicked"
        traces.sync_lead(status)
        mailing_id = traces.get_mailing(status)
        if mailing_id:
            scheduled = self.get_scheduled(mailing_id)
            mailing_id.action_send_mail([traces.res_id], scheduled_date=scheduled)

        return traces

    def set_replied(self, mail_mail_ids=None, mail_message_ids=None):
        """   """
        traces = super(MailingTrace, self).\
            set_replied(mail_mail_ids, mail_message_ids)
        status = "message_replied"
        traces.sync_lead(status)
        mailing_id = traces.get_mailing(status)
        if mailing_id:
            scheduled = self.get_scheduled(mailing_id)
            mailing_id.action_send_mail([traces.res_id], scheduled_date=scheduled)

        return traces

    def set_bounced(self, mail_mail_ids=None, mail_message_ids=None):
        """   """
        traces = super(MailingTrace, self).\
            set_bounced(mail_mail_ids, mail_message_ids)
        status = "message_bounced"
        traces.sync_lead(status)
        mailing_id = traces.get_mailing(status)
        if mailing_id:
            scheduled = self.get_scheduled(mailing_id)
            mailing_id.action_send_mail([traces.res_id], scheduled_date=scheduled)

        return traces

    def sync_lead(self, status):
        """ Buscar Lead/partner para atualizar o estágio das mesmas"""
        if self.email or self.sms_number:
            domain = [('team_id.name', 'ilike', 'Pré-Cadastros'), ('type', '=', 'opportunity')]
            email_or_mobile = OR([[('email_from', '=', self.email)], [('mobile', 'ilike', self.sms_number)]])
            res_domain = AND([email_or_mobile, domain])
            lead = self.env['crm.lead'].search(res_domain, limit=1)
            if not lead.campaign_id and self.campaign_id:
                lead.campaign_id = self.campaign_id.id

            if lead:
                if status == 'message_opened':
                    lead.update_stage(new_stage="Qualificado")
                elif status == 'message_clicked':
                    lead.update_stage(new_stage="Qualificado")
                elif status == 'message_replied':
                    lead.update_stage(new_stage="Proposição")
                elif status == 'message_bounced':
                    lead.active = False