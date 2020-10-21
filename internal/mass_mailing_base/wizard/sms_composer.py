# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SendSMS(models.TransientModel):
    _inherit = 'sms.composer'

    message_type = fields.Selection(
        selection=[
            ('whatsapp', 'WhatsApp'),
            ('sms', 'SMS'),
        ],
        string='Type',
    )

    def _action_send_sms_comment(self, records=None):
        """
        Sobrescrevi o método apenas para injetar o parametro message_type
        """
        records = records if records is not None else self._get_records()
        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')

        messages = self.env['mail.message']
        for record in records:
            messages |= record._message_sms(
                self.body, subtype_id=subtype_id,
                partner_ids=self.partner_ids.ids or False,
                number_field=self.number_field_name,
                sms_numbers=self.sanitized_numbers.split(',')
                if self.sanitized_numbers else None,
                message_type=self.message_type,
            )
        return messages

    def _prepare_recipient_values(self, records):
        """
        Sobrescrita de método para identificar o tipo de composer quando
        chamar o get recipients info
        """
        recipients_info = records._sms_get_recipients_info(
            force_field=self.number_field_name,
            message_type=self.message_type
        )
        return recipients_info
