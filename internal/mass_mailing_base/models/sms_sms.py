# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mass_mailing_base.tools import helpers

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

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
            ('input', 'Recebido'),
            ('output', 'Enviado'),
        ],
        default="output",
    )

    error_message = fields.Char(
        string="Mensagem de ERRO",
    )

    @api.model
    def create(self, values):
        sms_id = super(SmsSms, self).create(values)
        if sms_id.mail_message_id and sms_id.mail_message_id.message_type:
            sms_id.message_type = sms_id.mail_message_id.message_type
        return sms_id

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

        self.mail_message_id = message
        return message

    def _postprocess_iap_sent_sms(self, iap_results, failure_reason=None, delete_all=False):
            super(SmsSms, self).\
                _postprocess_iap_sent_sms(iap_results, failure_reason=failure_reason, delete_all=delete_all)

            sms_sms_model = self.env['sms.sms'].sudo()
            # Tratamento de rastreio em batch
            for service in ['sms', 'whatsapp']:
                sms_filtered_ids = sms_sms_model.search([('mailing_id', '!=', False), ('message_type', '=', service)])
                if not sms_filtered_ids:
                    continue

                iap_account = self.env["iap.account"].search([('name', '=', service)], limit=1)
                if iap_account:
                    SMS_STATES = iap_account.get_provider_states(type=service)
                else:
                    _logger.warning(f"Attention! No Provider for service: {service} - Take a lot at configuration")
                    continue

                for state in SMS_STATES.keys():
                    sms_iap_ids = [item['res_id'] for item in iap_results if item['state'] == state]
                    sms_ids = [item for item in sms_iap_ids if item in sms_filtered_ids]
                    traces = self.env['mailing.trace'].sudo().search([
                        ('sms_sms_id_int', 'in', sms_ids)
                    ])
                    if traces and state in ['sent', 'queued']:
                        traces.write({'sent': fields.Datetime.now(), 'exception': False})
                    elif traces:
                        traces.set_failed(failure_type=SMS_STATES[state])


