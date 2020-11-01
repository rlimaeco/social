# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo.addons.mass_mailing_base.tools import helpers

from odoo import models
from odoo.tools import html2plaintext, plaintext2html


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_sms(self, body, subtype_id=False, partner_ids=False,
                     number_field=False, sms_numbers=None,
                     sms_pid_to_number=None, message_type="sms", **kwargs):
        """ Sobrescrita de metodo para receber o message_type como parametro
        e passar para a funcao message_post o parametro e nao hardcode

        Main method to post a message on a record using SMS-based
        notification method.

        :param body: content of SMS;
        :param subtype_id: mail.message.subtype used in mail.message associated
          to the sms notification process;
        :param partner_ids: if set is a record set of partners to notify;
        :param number_field: if set is a name of field to use on current record
          to compute a number to notify;
        :param sms_numbers: see ``_notify_record_by_sms``;
        :param sms_pid_to_number: see ``_notify_record_by_sms``;
        """
        self.ensure_one()
        sms_pid_to_number = \
            sms_pid_to_number if sms_pid_to_number is not None else {}

        if number_field or (partner_ids is False and sms_numbers is None):
            info = self._sms_get_recipients_info(
                force_field=number_field, message_type=message_type)[self.id]
            info_partner_ids =\
                info['partner'].ids if info['partner'] else False
            info_number = \
                info['sanitized'] if info['sanitized'] else info['number']
            if info_partner_ids and info_number:
                sms_pid_to_number[info_partner_ids[0]] = info_number
            if info_partner_ids:
                partner_ids = info_partner_ids + (partner_ids or [])
            if info_number and not info_partner_ids:
                sms_numbers = [info_number] + (sms_numbers or [])

        if subtype_id is False:
            subtype_id = \
                self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')

        return self.message_post(
            body=plaintext2html(html2plaintext(body)),
            partner_ids=partner_ids or [],
            message_type=message_type, subtype_id=subtype_id,
            sms_numbers=sms_numbers, sms_pid_to_number=sms_pid_to_number,
            **kwargs
        )

    def _sms_get_recipients_info(self, force_field=False, message_type="sms"):
        """" Manipular numeros de destinatario"""
        recipients_info = \
            super(MailThread, self)._sms_get_recipients_info(force_field)

        for partner in self:
            info = recipients_info.get(partner.id)

            # Para SMS sempre Adicionar o número 9
            if message_type == "sms":
                s_number = helpers.valid_alternative_9number(info)
                if s_number:
                    recipients_info.get(partner.id).update(sanitized=s_number)
                    return recipients_info

            # Para whatsapp remover espaços em branco
            if message_type == "whatsapp":
                valid_number = helpers.valid_alternative_9number(info)
                if valid_number:
                    number = re.sub('[^0-9]', '', info.get("number"))

                    w_number = "+{}".format(number) \
                        if number[:2] == "55" else "+55{}".format(number)

                    recipients_info.get(partner.id).update(sanitized=w_number)
                    return recipients_info

        return recipients_info
