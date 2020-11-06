# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class Mailing(models.Model):

    _inherit = 'mailing.mailing'

    # mailing options
    mailing_type = fields.Selection(selection_add=[('whatsapp', 'Whatsapp')])

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

    def action_send_mail(self, res_ids=None):
        mass_sms = self.filtered(lambda m: m.mailing_type in ['sms', 'whatsapp'])
        if mass_sms:
            mass_sms.action_send_sms(res_ids=res_ids)
        return super(Mailing, self - mass_sms).action_send_mail(res_ids=res_ids)

    def action_send_sms(self, res_ids=None):
        for mailing in self:
            if not res_ids:
                res_ids = mailing._get_remaining_recipients()
            if not res_ids:
                raise UserError(_('There are no recipients selected.'))

            composer = self.env['sms.composer'].with_context(active_id=False).create(
                mailing._send_sms_get_composer_values(res_ids))
            if mailing.mailing_type == 'whatsapp':
                composer.message_type = 'whatsapp'
            else:
                composer.message_type = 'sms'
            composer._action_send_sms()
            mailing.write({'state': 'done', 'sent_date': fields.Datetime.now()})
        return True

