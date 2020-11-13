# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import threading

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class Mailing(models.Model):

    _inherit = 'mailing.mailing'

    # mailing options
    mailing_type = fields.Selection(selection_add=[("whatsapp", "Whatsapp")])

    trigger = fields.Selection(
        string="Type Trigger",
        selection=[
            ("message_opened", "Message: Opened"),
            ("message_not_opened", "Message: Not Opened"),
            ("message_replied", "Message: Replied"),
            ("message_not_replied", "Message: Not Replied"),
        ],
    )

    trigger_mailing_id = fields.Many2one(
        comodel_name="mailing.mailing",
        string="Activity Trigger",
    )

    trigger_qty_time = fields.Integer(
        string="Quantidade para acionar"
    )
    
    trigger_type_time = fields.Selection(
        string="Type Time Trigger",
        selection=[
            ("hours", "Hours"),
            ("days", "Days"),
        ],
        default="days"
    )

    template_mail_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template",
    )

    @api.model
    def default_get(self, fields):
        res = super(Mailing, self).default_get(fields)
        if fields is not None and 'keep_archives' in fields and res.get('mailing_type') in ['sms', 'whatsapp']:
            res['keep_archives'] = True
        return res

    @api.onchange('mailing_type')
    def _onchange_mailing_type(self):
        """ Force utm_medium in mailing"""
        utm_medium_email = self.env.ref('utm.utm_medium_email')
        utm_medium_sms = self.env.ref('mass_mailing_sms.utm_medium_sms')
        utm_medium_whatsapp = self.env.ref('mass_mailing_base.utm_medium_whatsapp')

        if self.mailing_type == 'sms' and (
                not self.medium_id or self.medium_id in [utm_medium_email, utm_medium_whatsapp]
        ):
            self.medium_id = utm_medium_sms.id
        elif self.mailing_type == 'whatsapp' and (
                not self.medium_id or self.medium_id in [utm_medium_email, utm_medium_sms]
        ):
            self.medium_id = utm_medium_whatsapp.id
        elif self.mailing_type == 'mail' and (
                not self.medium_id or self.medium_id in [utm_medium_sms, utm_medium_whatsapp]
        ):
            self.medium_id = utm_medium_email.id

    @api.model
    def create(self, values):
        if values.get('mailing_type') == 'whatsapp':
            if not values.get('medium_id'):
                values['medium_id'] = self.env.ref('mass_mailing_base.utm_medium_whatsapp').id
            # TODO: Templates para mensagens whatsapp como no sms exibido nas duas linhas abaixo:
            # if values.get('sms_template_id') and not values.get('body_plaintext'):
            #     values['body_plaintext'] = self.env['sms.template'].browse(values['sms_template_id']).body
        return super(Mailing, self).create(values)

    def action_send_mail(self, res_ids=None, scheduled_date=None):
        """
        Sobrescrita de método para injetar o parametro de agendamento de email
        """
        mass_sms = self.filtered(
            lambda m: m.mailing_type in ['sms', 'whatsapp'])
        if mass_sms:
            mass_sms.action_send_sms(
                res_ids=res_ids, scheduled_date=scheduled_date)

        if not scheduled_date:
            res = super(
                Mailing, self - mass_sms).action_send_mail(res_ids=res_ids)
            return res

        author_id = self.env.user.partner_id.id

        for mailing in self:
            if not res_ids:
                res_ids = mailing._get_remaining_recipients()
            if not res_ids:
                raise UserError(_('There are no recipients selected.'))

            composer_values = {
                'author_id': author_id,
                'attachment_ids':
                    [(4, attachment.id) for attachment in mailing.attachment_ids],
                'body': mailing.body_html,
                'subject': mailing.subject,
                'model': mailing.mailing_model_real,
                'email_from': mailing.email_from,
                'record_name': False,
                'composition_mode': 'mass_mail',
                'mass_mailing_id': mailing.id,
                'mailing_list_ids':
                    [(4, l.id) for l in mailing.contact_list_ids],
                'no_auto_thread': mailing.reply_to_mode != 'thread',
                'template_id': None,
                'mail_server_id': mailing.mail_server_id.id,
                'scheduled_date': scheduled_date,
            }
            if mailing.reply_to_mode == 'email':
                composer_values['reply_to'] = mailing.reply_to

            composer = self.env['mail.compose.message'].with_context(
                active_ids=res_ids).create(composer_values)
            extra_context = self._get_mass_mailing_context()
            composer = composer.with_context(
                active_ids=res_ids, **extra_context)

            all_mail_values = composer.get_mail_values(res_ids)
            batch_mails = self.env['mail.mail']

            for res_id, mail_values in all_mail_values.items():
                batch_mails |= batch_mails.create(mail_values)

            return batch_mails

    def action_send_sms(self, res_ids=None, scheduled_date=None):
        """
        Inject message_type and scheduled date in action_send_sms
        """
        for mailing in self:
            if not res_ids:
                res_ids = mailing._get_remaining_recipients()
            if not res_ids:
                raise UserError(_('There are no recipients selected.'))

            composer = self.env['sms.composer'].\
                with_context(active_id=False).create(
                mailing._send_sms_get_composer_values(res_ids))
            if mailing.mailing_type == 'whatsapp':
                composer.message_type = 'whatsapp'
            else:
                composer.message_type = 'sms'

            if scheduled_date:
                composer.scheduled_date = scheduled_date

            composer._action_send_sms()
            mailing.write(
                {'state': 'done', 'sent_date': fields.Datetime.now()}
            )
        return True

