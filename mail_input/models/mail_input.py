# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>

import re

from odoo import api, fields, models
from odoo.tools import html2plaintext


class MailInput(models.Model):
    _name = 'mail.input'
    _inherit = ['mail.thread']
    _description = "Receive emails in partner's messages"

    partner_id = fields.Many2one(
        string='Related Partner',
        comodel_name='res.partner',
        required=True,
        ondelete='cascade',
        index=True,
    )

    subject = fields.Char('Subject')
    email_from = fields.Char('From')

    def name_get(self):
        """
            Define name of mail input as part of message's subject
        """
        result = []
        for rec in self:
            if len(rec.subject) > 30:
                name = f'{rec.subject[:30]}...'
            else:
                name = rec.subject

            result.append((rec.id, name))
        return result

    def create_mail_in_lead(self, msg, lead, partner=False):
        """Criar mail message no crm.lead"""
        mail_message_model = self.env['mail.message'].sudo()

        msg_data ={
            'subject': msg.get('subject'),
            'body': msg.get('body'),
            'res_id': lead.id,
            'model': 'crm.lead',
            'message_type': 'email',
            'email_from': partner.email if partner else False,
            'author_id': partner.id if partner else False
        }
        message = mail_message_model.create(msg_data)
        return message or False

    @staticmethod
    def get_infos_from_msg(msg):
        email_from_str = msg.get('email_from', False)

        if email_from_str:
            try:
                name_from = re.findall(r'\"(.+?)\"', email_from_str)[0]
                email_from = re.findall('\S+@\S+', email_from_str)[0][1:-1]
                return [name_from, email_from]
            except Exception:
                return False
        else:
            return False

    def find_and_attach_to_lead(self, msg):
        """ Buscar Lead/partner para anexar mensagem de entrada"""

        name_from, email_from = self.get_infos_from_msg(msg)

        if name_from and email_from:

            desc = html2plaintext(msg.get("body")) if msg.get("body") else ""

            lead = self.env['crm.lead'].search([
                ('email_from', '=', email_from)], limit=1)

            if not lead.partner_id:
                partner = self.env['res.partner'].search([('email', '=', email_from)], limit=1)
                if not partner:
                    partner = self.env['res.partner'].create({
                        'name': name_from,
                        'email': email_from
                    })
            else:
                partner = lead.partner_id

            if not lead:
                lead = self.env["crm.lead"].create(
                    {
                        "type": "opportunity",
                        "name": msg.get('subject'),
                        "partner_name": name_from,
                        "partner_id": partner.id,
                        "email_from": email_from,
                        "description": desc,
                    }
                )
            else:
                # Qualifica Lead
                new_stage_id = lead.get_stage(partial_name="Novo")
                if lead.stage_id.id == new_stage_id:
                    lead.update_stage(new_stage="Qualificado")

            self.create_mail_in_lead(msg, lead, partner=partner)

            return lead
        else:
            return False

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        create_context, defaults = self.prepare_lead_update(msg_dict)

        return super(MailInput, self.with_context(create_context)).message_new(msg_dict, custom_values=defaults)

    def message_update(self, msg_dict, update_vals=None):
        """Called by ``message_process`` when a new message is received
           for an existing thread. The default behavior is to update the record
           with update_vals taken from the incoming email.
           Additional behavior may be implemented by overriding this
           method.
           :param dict msg_dict: a map containing the email details and
                               attachments. See ``message_process`` and
                               ``mail.message.parse()`` for details.
           :param dict update_vals: a dict containing values to update records
                              given their ids; if the dict is None or is
                              void, no write operation is performed.
        """
        create_context, defaults = self.prepare_lead_update(msg_dict)

        return super(MailInput, self.with_context(create_context)).message_update(msg_dict, update_vals=defaults)

    def prepare_lead_update(self, msg_dict):
        create_context = dict(self.env.context or {})
        create_context['default_user_id'] = False

        lead = self.find_and_attach_to_lead(msg_dict)

        defaults = {
            'partner_id': lead.partner_id.id,
            'subject': lead.name,
            'email_from': lead.email_from
        }

        create_context['mail_create_nolog'] = "True"
        # create_context['mail_create_nosubscribe'] = "True"
        # create_context['mail_notrack'] = "True"
        return create_context, defaults
