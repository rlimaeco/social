# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SendSMS(models.TransientModel):
    _inherit = 'sms.composer'

    message_type = fields.Selection(
        selection=[
            ('whatsapp', 'WhatsApp'),
            ('sms', 'SMS'),
        ],
        string='Message Type',
    )

    scheduled_date = fields.Char(
        string='Scheduled Send Date',
        help="If set, the queue manager will send the email after the date."
             " If not set, the email will be send as soon as possible.",
    )

    def _action_send_sms_comment(self, records=None):
        """ Just inject param message_type """
        records = records if records is not None else self._get_records()
        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')

        messages = self.env['mail.message']
        for record in records:
            messages |= record._message_sms(
                self.body, subtype_id=subtype_id,
                partner_ids=False,
                number_field=self.number_field_name,
                sms_numbers=self.sanitized_numbers.split(',')
                if self.sanitized_numbers else None,
                message_type=self.message_type,
            )
        return messages

    def _prepare_mass_sms_trace_values(self, record, sms_values):
        res = super(SendSMS, self)._prepare_mass_sms_trace_values(record, sms_values)
        if self.message_type == 'whatsapp':
            res['trace_type'] = 'whatsapp'
        return res

    def _prepare_mass_sms_values(self, records):
        """ Injetar message_type na criacao em massa"""
        result = super(SendSMS, self)._prepare_mass_sms_values(records)
        if self.composition_mode == 'mass' and self.message_type:
            for record in records:
                sms_values = result[record.id]
                sms_values.update({
                    'message_type': self.message_type,
                    "scheduled_date": self.scheduled_date,
                })
        return result

    # def _prepare_recipient_values(self, records):
    #     """
    #     Sobrescrita de método para identificar o tipo de composer quando
    #     chamar o get recipients info
    #     """
    #     recipients_info = records._sms_get_recipients_info(
    #         force_field=self.number_field_name,
    #         message_type=self.message_type
    #     )
    #     return recipients_info
