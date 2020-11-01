# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mass_mailing_base.tools import helpers

from odoo import fields, models


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    message_id = fields.Char(string="SMS ID")

    state = fields.Selection(
        selection_add=[
            ('received', 'Recebida'),
            ('read', 'Lido'),
        ]
    )

    message_type = fields.Selection(
        string="Message Type",
        selection=[
            ('sms', 'SMS Phone'),
            ('whatsapp', 'WhatsApp'),
        ],
    )

    type = fields.Selection(
        string="Tipo de SMS",
        selection=[
            ('input', 'Entrada/recebido'),
            ('output', 'Saída/Enviado'),
        ],
        default="output",
    )

    def create_mail_message(self, model, partner_id=False):
        """Criar mail message no modelo"""
        mail_message_model = self.env['mail.message'].sudo()

        message = mail_message_model.create({
            'subject': 'Message',
            'body': self.body,
            'res_id': model.id,
            'model': model._name,
            'message_type':
                self.message_type if partner_id else "notification",
            "message_id": self.id,
            'email_from': partner_id.email if partner_id else False,
            'author_id': partner_id.id if partner_id else False,
        })
        return message or False


    def find_and_attach_to_lead(self):
        """ Buscar Lead/partner para anexar mensagem de entrada"""

        res_partner_model = self.env['res.partner'].sudo()
        crm_lead_model = self.env['crm.lead'].sudo()

        lead_id = helpers.get_record_from_number(crm_lead_model, self.number)

        # Se já existe uma LEAD, adiciona SMS na thread de comunicação
        if lead_id:
            message = self.create_mail_message(
                model=lead_id,
                partner_id=lead_id.partner_id,
            )

        # Senão, buscar pelo partner e gerar nova LEAD
        else:
            partner_id = helpers.get_record_from_number(
                res_partner_model, self.number)
            if partner_id:

                # Imitate what happens in the controller when somebody
                # creates a new lead from the website form
                lead_id = crm_lead_model.with_context(
                    mail_create_nosubscribe=True).create({
                    "name": "New LEAD from {}".format(self.message_type),
                    "partner_id": partner_id.id,
                    "partner_name": partner_id.name,
                })

                message = self.create_mail_message(
                    model=lead_id,
                    partner_id=lead_id.partner_id,
                )

            # Senão gerar LEAD sem partner mas com numero setado
            else:

                lead_id = self.env['crm.lead'].with_context(
                    mail_create_nosubscribe=True).sudo().create({
                    "name": "New LEAD from {}".format(self.number),
                    "mobile": self.number,
                })
                message = self.create_mail_message(model=lead_id)

        return message
