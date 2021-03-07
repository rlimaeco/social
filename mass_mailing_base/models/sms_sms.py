# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import logging
import threading

from odoo.addons.mass_mailing_base.tools import helpers

from odoo import api, fields, models
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    message_id = fields.Char(string="SMS ID")

    state = fields.Selection(
        selection_add=[
            ('received', 'Received'),
        ],
        ondelete={'received': 'set default'},
    )

    message_type = fields.Selection(
        string="Message Type",
        selection=[
            ('sms', 'SMS Phone'),
            ('whatsapp', 'WhatsApp'),
        ],
    )

    direction_type = fields.Selection(
        string="SMS Type",
        selection=[
            ('input', 'Received'),
            ('output', 'Sent'),
        ],
        default="output",
    )

    error_message = fields.Char(
        string="Error Message",
    )

    scheduled_date = fields.Char(
        string='Scheduled Send Date',
        help="If set, the queue manager will send the email after the date."
             " If not set, the email will be send as soon as possible.",
    )

    @api.model
    def _process_queue(self, ids=None):
        """  """

        domain = ['&',
                 ('state', '=', 'outgoing'),
                 '|',
                 ('scheduled_date', '<', datetime.datetime.now()),
                 ('scheduled_date', '=', False)]

        filtered_ids = self.search(domain, limit=10000).ids

        if ids:
            ids = list(set(filtered_ids) & set(ids))
        else:
            ids = filtered_ids
        ids.sort()

        res = None
        try:
            # auto-commit except in testing mode
            auto_commit = not getattr(threading.currentThread(), 'testing', False)
            res = self.browse(ids).send(delete_all=False, auto_commit=auto_commit, raise_exception=False)
        except Exception:
            _logger.exception("Failed processing SMS queue")
        return res

    @api.model
    def create(self, values):
        sms_id = super(SmsSms, self).create(values)
        if sms_id.mail_message_id and sms_id.mail_message_id.message_type:
            sms_id.message_type = sms_id.mail_message_id.message_type

        # Função que verifica se SMS criado é devido a alguma resposta
        # de SMS ja enviado anteriormente
        if sms_id.direction_type == "input":
            sms_id.set_reply_mailing_trace()
        return sms_id

    def create_mail_message(self, model, partner_id=False):
        """Criar mail message no modelo"""
        mail_message_model = self.env['mail.message'].sudo()
        msg_data = {
            'subject': 'Message',
            'res_id': model.id,
            'model': model._name,
            "message_id": self.id,
        }
        if partner_id:
            msg_data["body"] = self.prepare_message_body()
            msg_data["message_type"] = self.message_type
            msg_data["email_from"] = partner_id.email
            msg_data["author_id"] = partner_id.id
        else:
            msg_data["message_type"] = "notification"
            msg_data["body"] = self.body

        message = mail_message_model.create(msg_data)
        return message or False

    def set_lang_context(self):
        admin_user = self.env['res.users'].sudo().search([
            ('id', '=', self.env.ref('base.user_admin').id)], limit=1
        )
        if admin_user:
            self.env.context = self.with_context(lang=admin_user.lang).env.context

    def prepare_message_body(self):
        origin_label = _('Origin')
        message_label = _('Message')
        body = f"<b>{origin_label}</b>: {self.message_type.capitalize()}<br>" \
               f"<b>{message_label}</b>: {self.body}"
        return body

    def find_and_attach_to_lead(self):
        """ Buscar Lead/partner para anexar mensagem de entrada"""

        res_partner_model = self.env['res.partner'].sudo()
        crm_lead_model = self.env['crm.lead'].sudo()
        self.set_lang_context()

        lead_id = helpers.get_record_from_number(crm_lead_model, self.number)

        if lead_id:
            # Se já existe uma LEAD, adiciona SMS na thread de comunicação
            message = self.create_mail_message(
                model=lead_id,
                partner_id=lead_id.partner_id,
            )
        else:
            # Senão, buscar pelo partner e gerar nova LEAD
            presignup = self.env['crm.stage'].search([], limit=1, order="sequence asc")
            partner_id = helpers.get_record_from_number(
                res_partner_model, self.number)
            if partner_id:

                # Imitate what happens in the controller when somebody
                # creates a new lead from the website form
                lead_id = crm_lead_model.with_context(
                    mail_create_nosubscribe=True).create({
                    "name": _("LEAD via {}").format(self.message_type),
                    "partner_id": partner_id.id,
                    "partner_name": partner_id.name,
                    "mobile": partner_id.mobile,
                    "phone": partner_id.mobile,
                    "lead_type": "presignup",
                    "type": "opportunity",
                    "team_id": presignup.team_id.id
                })

                message = self.create_mail_message(
                    model=lead_id,
                    partner_id=lead_id.partner_id,
                )

            else:
                # Senão gerar LEAD sem partner mas com numero setado

                lead_id = self.env['crm.lead'].with_context(
                    mail_create_nosubscribe=True).sudo().create({
                    "name": _("LEAD from {}").format(self.number),
                    "mobile": self.number,
                    "phone": self.number,
                    "lead_type": "presignup",
                    "type": "opportunity",
                    "team_id": presignup.team_id.id
                })
                message = self.create_mail_message(model=lead_id)

        self.mail_message_id = message
        return message

    def set_reply_mailing_trace(self):
        """ Verificar se existe envio de mensagem com mesmo numero.
        Se existir o envio de mensagem, setar mensagem como respondida  """

        trace_id = self.env["mailing.trace"].sudo().search([
            ("sms_number", "like", "%{}".format(self.number[-8:])),
            ("trace_type", "=", self.message_type),
            ("sent", "!=", False),
        ], limit=1,  order="sent desc")

        if trace_id:
            # Se nao identificou leitura,
            if not trace_id.opened:
                trace_id.set_opened()

            # Marcar como respondido
            trace_id.set_replied()

    def set_sent(self):
        """   """
        self.state = "sent"
        for trace_id in self.mailing_trace_ids:
            trace_id.set_sent()

    def set_opened(self):
        """   """
        for trace_id in self.mailing_trace_ids:
            trace_id.set_opened()

    def set_clicked(self):
        """   """
        self.set_opened()
        for trace_id in self.mailing_trace_ids:
            trace_id.set_clicked()

    def set_replied(self):
        """   """
        self.set_opened()
        for trace_id in self.mailing_trace_ids:
            trace_id.set_replied()

    def set_bounced(self):
        for trace_id in self.mailing_trace_ids:
            trace_id.set_bounced()
