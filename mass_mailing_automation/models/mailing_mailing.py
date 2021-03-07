# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.osv.expression import AND

_logger = logging.getLogger(__name__)


def get_status_domain(trigger, domain):
    status_field = {
        'message_opened': ('opened', '!=', False),
        'message_clicked': ('clicked', '!=', False),
        'message_replied': ('replied', '!=', False),
        'message_not_opened': ('opened', '=', False),
        'message_not_replied': ('replied', '=', False)
    }
    return AND([[status_field.get(trigger, False)],domain]) if status_field.get(trigger, False) else False


class Mailing(models.Model):

    _inherit = 'mailing.mailing'

    template_mail_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template",
    )

    body_html = fields.Html(
        string='Body converted to be send by mail',
        sanitize_attributes=False,
        compute="compute_body_html",
    )

    trigger = fields.Selection(
        string="Type Trigger",
        selection=[
            ("campaign_start", "Início da campanha"),
            ("message_opened", "Mensagem aberta"),
            ("message_clicked", "Mensagem clicada"),
            ("message_replied", "Mensagem respondida"),
            ("message_not_opened", "Mensagem não aberta"),
            ("message_not_replied", "Mensagem não respondida"),
        ],
        default="campaign_start",
    )

    trigger_mailing_id = fields.Many2one(
        comodel_name="mailing.mailing",
        string="Activity Trigger",
    )

    trigger_qty_time = fields.Integer(
        string="Quantidade para acionar" # Pode ser Intervalo de Disparo ?
    )

    trigger_type_time = fields.Selection(
        string="Type Time Trigger",
        selection=[
            ("minutes", "Minutos(s)"),
            ("hours", "Hora(s)"),
            ("days", "Dias(s)"),
        ],
        default="minutes"
    )

    mailing_model_real = fields.Char(related='campaign_id.mailing_model_real')

    mailing_model_id = fields.Many2one(related='campaign_id.mailing_model_id')

    mailing_model_name = fields.Char(related='campaign_id.mailing_model_name')

    mailing_domain = fields.Char(related='campaign_id.mailing_domain')

    contact_list_ids = fields.Many2many(related='campaign_id.contact_list_ids')

    sequence = fields.Integer(
        string='Sequence', default=0
    )

    state = fields.Selection(
        selection_add=[
            ('stopped', 'Stopped')
        ], ondelete={'stopped': 'set default'}
    )

    ir_actions_server_id = fields.Many2one(
        comodel_name='ir.actions.server',
        string='Server action',
    )

    @api.onchange('template_mail_id')
    def _onchange_template_mail_id(self):
        """   """
        for record in self:
            if record.template_mail_id:
                record.body_html = record.template_mail_id.body_html
                record.name = record.template_mail_id.subject

    @api.depends("template_mail_id")
    def compute_body_html(self):
        for record in self:
            if record.template_mail_id:
                record.body_html = record.template_mail_id.body_html

    @api.onchange('name')
    def _onchange_name(self):
        """   """
        for record in self:
            record.subject = record.name

    def _get_recipients(self):
        """ Get recipients from campaign """

        if self.mailing_domain:
            domain = safe_eval(self.mailing_domain)
            try:
                list_ids = domain[0][2]
                if self.contact_list_ids.ids != list_ids and isinstance(list_ids, list):
                    domain = [('list_ids', 'in', self.contact_list_ids.ids)]
                res_ids = self.env[self.mailing_model_real].search(domain).ids
            except ValueError:
                res_ids = []
                _logger.exception('Cannot get the mass mailing recipients, model: %s, domain: %s',
                                  self.mailing_model_real, domain)
        else:
            res_ids = []

        return res_ids

    def _compute_statistics(self):
        try:
            obj_fields = [
                'scheduled', 'expected', 'ignored', 'sent',
                'delivered', 'opened', 'clicked', 'replied',
                'bounced', 'failed', 'received_ratio',
                'opened_ratio', 'replied_ratio', 'bounced_ratio'
            ]
            for obj in self:
                for field_name in obj_fields:
                    if getattr(obj, field_name) is None:
                        setattr(obj, field_name, 0)

            return super(Mailing, self)._compute_statistics()

        except Exception as e:
            _logger.exception(str(e))

    def _get_remaining_recipients(self):
        res_ids = super(Mailing, self)._get_remaining_recipients()

        if self.trigger_mailing_id:
            domain = [
                ('model', '=', self.mailing_model_real),
                ('res_id', 'in', res_ids),
                ('mass_mailing_id', '=', self.trigger_mailing_id.id)
            ]
            status_domain = get_status_domain(self.trigger, domain)
            if status_domain:
                tracking = self.env['mailing.trace'].search_read(status_domain, ['res_id'])
                missing_res_ids = {record['res_id'] for record in tracking}
                new_res_ids = [rid for rid in res_ids if rid in missing_res_ids]
                if new_res_ids is None:
                    new_res_ids = []
                return new_res_ids
            else:
                if res_ids is not None:
                    return res_ids
                else:
                    return []
        else:
            return res_ids

    def action_create_activity(self):
        """   """
        return {'type': 'ir.actions.act_window_close'}

    def action_edit_activity(self):
        """   """
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }