# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.addons.mass_mailing.models.mailing import MASS_MAILING_BUSINESS_MODELS
from ast import literal_eval
from odoo.osv.expression import AND
from odoo.addons.mass_mailing_automation.tools import helpers


class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    def get_stage_ids_from_state(self, sent=False, stopped=False):
        if sent:
            return self.stage_id.search([
                '|', '|',
                ('name', 'ilike', _('Schedule')),
                ('name', 'ilike', _('Sending')),
                ('name', 'ilike', _('Sent'))
            ]).ids
        elif stopped:
            return self.stage_id.search([
                ('name', 'ilike', _('Stopped'))
            ]).ids
        else:
            return self.stage_id.search([
                '|',
                ('name', 'ilike', _('New')),
                ('name', 'ilike', _('Design'))
            ]).ids

    mailing_model_real = fields.Char(
        compute='_compute_model',
        string='Recipients Real Model',
        default='mailing.contact',
        required=True
    )
    mailing_model_id = fields.Many2one(
        'ir.model',
        string='Recipients Model',
        domain=[('model', 'in', MASS_MAILING_BUSINESS_MODELS)],
        default=lambda self: self.env.ref('mass_mailing.model_mailing_list').id
    )
    mailing_model_name = fields.Char(
        related='mailing_model_id.model',
        string='Recipients Model Name',
        readonly=True,
        related_sudo=True
    )
    mailing_domain = fields.Char(string='Domain', default=[])

    contact_list_ids = fields.Many2many(
        'mailing.list',
        'mass_utm_campaign_list_rel',
        string='Mailing Lists', copy=True
    )

    crm_lead_count = fields.Integer(
        string='Lead Count total',
        compute='_compute_crm_lead_count',
    )

    related_campaign_id = fields.Many2one(
        comodel_name="utm.campaign",
        string="Related Campaigns",
        domain=lambda self: [('stage_id.id', 'in',
                              self.get_stage_ids_from_state(sent=True))
                             ]
    )
    use_related_campaign = fields.Boolean(string="Use Contacts from other Campaign", default=False)

    trigger_related_campaign = fields.Selection(
        string="Trigger Filter",
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

    current_stage = fields.Char(string='Current Stage', compute="_compute_current_stage")

    @api.onchange('related_campaign_id')
    def _onchange_related_campaign(self):
        if self.related_campaign_id:
            self.mailing_model_id = self.related_campaign_id.mailing_model_id
            self.mailing_model_name = self.related_campaign_id.mailing_model_name
            self.mailing_domain = self.related_campaign_id.mailing_domain
            self.contact_list_ids = self.related_campaign_id.contact_list_ids
            self.update_contacts_campaign()

    @api.onchange('trigger_related_campaign')
    def _onchange_trigger_related_campaign(self):
        self.update_contacts_campaign()

    def update_contacts_campaign(self):
        if len(self.contact_list_ids) > 0:
            self.filter_related_contacts(self.trigger_related_campaign)

    @api.depends('mailing_model_id', 'mailing_model_name')
    def _compute_model(self):
        for record in self:
            record.mailing_model_real = (record.mailing_model_name != 'mailing.list') and record.mailing_model_name or 'mailing.contact'

    @api.depends('stage_id')
    def _compute_current_stage(self):
        new_stages = self.get_stage_ids_from_state()
        sent_stages = self.get_stage_ids_from_state(sent=True)
        stopped_stages = self.get_stage_ids_from_state(stopped=True)
        for record in self:
            if record.stage_id.id in new_stages:
                record.current_stage = 'new'
            elif record.stage_id.id in sent_stages:
                record.current_stage = 'sent'
            elif record.stage_id.id in stopped_stages:
                record.current_stage = 'stopped'
            # Verifica status das atividades para atualizar o estágio da campanha
            record.check_sent_activities()

    @api.onchange('mailing_model_name', 'contact_list_ids')
    def _onchange_model_and_list(self):
        mailing_domain = literal_eval(self.mailing_domain) if self.mailing_domain else []
        if self.mailing_model_name:
            if mailing_domain:
                try:
                    self.env[self.mailing_model_name].search(mailing_domain, limit=1)
                except:
                    mailing_domain = []
            if not mailing_domain:
                if self.mailing_model_name == 'mailing.list' and self.contact_list_ids:
                    mailing_domain = [('list_ids', 'in', self.contact_list_ids.ids)]

                elif 'is_blacklisted' in self.env[self.mailing_model_name]._fields and not self.mailing_domain:
                    mailing_domain = [('is_blacklisted', '=', False)]
                elif 'opt_out' in self.env[self.mailing_model_name]._fields and not self.mailing_domain:
                    mailing_domain = [('opt_out', '=', False)]
        else:
            mailing_domain = []
        self.mailing_domain = repr(mailing_domain)

    def _compute_crm_lead_count(self):
        for record in self:
            record.crm_lead_count = self.env['crm.lead'] \
                .with_context(active_test=False) \
                .search_count([('campaign_id', '=', record.id)])

    def action_redirect_to_leads(self):
        action = self.env.ref('crm.crm_lead_all_leads').read()[0]
        action['domain'] = [('campaign_id', '=', self.id)]
        action['context'] = {'default_type': 'lead', 'active_test': False}
        return action

    def prepare_action_wizard_mailing(self, type):

        context = {
            'default_mailing_type': type,
            'search_default_assigned_to_me': 1,
            'search_default_campaign_id': self.id,
            'default_user_id': self.env.user.id,
            'mailing_sms': True,
            'default_campaign_id': self.id,
            'action_create_activity': True,
        }

        if type == 'whatsapp':
            name = f"New Activity using {type.capitalize()}"
        elif type == 'sms':
            name = f"New Activity using {type.upper()}"
        else:
            name = "New Activity using E-mail"

        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mailing.mailing',
            'view_id':  self.env.ref('mass_mailing_automation.mailing_mailing_view_form').id,
            'target': 'new',
            'context': context
        }

    def action_wizard_mailing_whatsapp(self):
        return self.prepare_action_wizard_mailing('whatsapp')

    def action_wizard_mailing_sms(self):
        return self.prepare_action_wizard_mailing('sms')

    def action_wizard_mailing_mail(self):
        return self.prepare_action_wizard_mailing('mail')

    def action_start_campaign(self):
        if not any(self.mailing_activities_ids):
            raise ValidationError(_('You must set up at least one activity to start this campaign.'))
        stage_sending = self.env['utm.stage'].search([('name', '=', _('Sending'))], limit=1)
        if self.execute(action='start'):
            self.write({'stage_id': stage_sending.id})

    def action_schedule_campaign(self):
        stage_schedule = self.env['utm.stage'].search([('name', '=', _('Schedule'))], limit=1)
        self.write({'stage_id': stage_schedule.id})

        action = self.env.ref('mass_mailing_automation.model_utm_campaign_schedule_date').read()[0]

        return {
            'name': action['name'],
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'utm.campaign.schedule.date',
            'view_id':  self.env.ref('mass_mailing_automation.mass_mailing_schedule_date_view_form').id,
            'target': 'new',
            'context': dict(self.env.context, default_utm_campaign_id=self.id)
        }

    def action_stop_campaign(self):
        stage_stopped = self.env['utm.stage'].search([], limit=1, order='sequence desc')
        if self.execute(action='stop'):
            self.write({'stage_id': stage_stopped.id})

    def execute(self, action):

        start_activity_ids = self.mailing_activities_ids.filtered(lambda m: m.trigger == 'campaign_start')
        updated = False

        for start_activity in start_activity_ids:
            if action == 'start':
                if start_activity.state == 'draft':
                    if not start_activity.schedule_date:
                        start_activity.schedule_date = self.get_scheduled(start_activity)
                    start_activity.action_put_in_queue()
                    updated = True
            elif action == 'stop':
                start_activity.state = 'stopped'
                updated = True

            self.set_children_activity_states(start_activity)

        return updated

    def set_children_activity_states(self, parent_activity, schedule=False):
        child_activity_ids = self.mailing_activities_ids.filtered(
            lambda m: m.trigger_mailing_id.id == parent_activity.id)

        for child in child_activity_ids:
            if parent_activity.state == 'stopped':
                child.schedule_date = False
                child.state = 'stopped'
            elif child.state == 'draft':
                if not schedule:
                    parent_date = parent_activity.schedule_date or parent_activity.sent_date
                else:
                    parent_date = schedule
                child.schedule_date = self.get_scheduled(child, start_date=parent_date)
                child.state = 'in_queue'

            next_activity_ids = self.mailing_activities_ids.filtered(lambda m: m.trigger_mailing_id.id == child.id)
            if len(next_activity_ids) > 0:
                self.set_children_activity_states(child)

    @staticmethod
    def get_scheduled(mailing_id, start_date=False):
        scheduled = fields.Datetime.now() if not start_date else start_date
        return helpers.define_time_trigger(mailing_id, scheduled)

    def filter_related_contacts(self, filter):

        for mailing_list in self.related_campaign_id.contact_list_ids:

            res_ids = mailing_list.contact_ids.ids
            domain = [
                ('model', '=', 'mailing.contact'),
                ('res_id', 'in', res_ids),
                ('campaign_id', '=', self.related_campaign_id.id)]

            if filter == 'message_opened':
                search_domain = AND([domain, [('state', '=', 'opened')]])
            elif filter == 'message_clicked':
                search_domain = AND([domain, [('clicked', '!=', False)]])
            elif filter == 'message_replied':
                search_domain = AND([domain, [('state', '=', 'replied')]])
            elif filter == 'message_not_opened':
                search_domain = AND([
                    domain,
                    [('state', 'in', ['ignored', 'exception', 'bounced'])]
                 ])
            elif filter == 'message_not_replied':
                search_domain = AND([
                    domain, [('replied', '=', False), ('state', '!=', 'replied')]
                ])
            else:
                search_domain = domain

            matched_trace = self.env['mailing.trace'].search_read(search_domain, ['res_id'])
            missing_res_ids = {record['res_id'] for record in matched_trace}
            filtered_res_ids = [rid for rid in res_ids if rid in missing_res_ids]

            if len(filtered_res_ids) > 0:
                id_campaign = self.id.origin if not isinstance(self.id, int) else self.id
                mtype = _('Filtred:')
                if not id_campaign:
                    mtype = _('Related:')
                    id_campaign = self.related_campaign_id.id
                name_campaign = f"L{id_campaign} - {mtype} {mailing_list.name}"
                existing_mailing_list = self.env['mailing.list'].search([('name', 'like', name_campaign)], limit=1)
                if not existing_mailing_list:
                    new_mailing_list = self.env['mailing.list'].create({
                        'name': name_campaign,
                        'is_public': mailing_list.is_public,
                        'contact_ids': [(6, 0, filtered_res_ids)],
                    })
                    if new_mailing_list:
                        self.contact_list_ids = [(6, 0, [new_mailing_list.id])]
                        self.mailing_activities_ids.write({'contact_list_ids': [(6, 0, [new_mailing_list.id])]})
                        self.notify_user(
                            title=_("Contacts List Created"),
                            msg=_("The contact list was successfully created!"),
                            type='success'
                        )
                else:
                    update_contacts = existing_mailing_list.write({'contact_ids': [(6, 0, filtered_res_ids)]})
                    if update_contacts:
                        self.contact_list_ids = [(6, 0, [existing_mailing_list.id])]

                        self.notify_user(
                            title=_("Contacts List Updated"),
                            msg=_("The contact list was updated with filtered contacts!"),
                            type='success'
                        )
            else:
                self.notify_user(
                    title=_("Attention"),
                    msg=_("No filter applied in contact list"),
                    type='error',
                    sticky=True
                )

    def notify_user(self, title, msg, type, sticky=False):
        msg_data = {
            "message": msg, "title": title, "sticky": sticky
        }
        if type == 'success':
            self.env.user.notify_success(**msg_data)
        elif type == 'error':
            self.env.user.notify_warning(**msg_data)
        elif type == 'danger':
            self.env.user.notify_danger(**msg_data)

    def write(self, values):
        res = super(UtmCampaign, self).write(values)
        # self.check_sent_activities()
        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        stage_new = self.env['utm.stage'].search([('name', '=', _('New'))], limit=1)

        default = dict(default or {},
                       name=_('%s (copy)') % self.name,
                       stage_id=stage_new.id,
                       contact_list_ids=self.contact_list_ids.ids
                       )

        campaign = super(UtmCampaign, self).copy(default=default)

        self.find_trigger_mailing_parent(campaign)

        # Re-evaluating the domain
        campaign._onchange_model_and_list()
        return campaign

    def check_sent_activities(self):
        sent_activity_ids = self.mailing_activities_ids.filtered(
            lambda m: m.state in ['sent', 'done'])
        if any(sent_activity_ids):
            stage_sent = self.env['utm.stage'].search([('name', '=', _('Sent'))], limit=1)
            if stage_sent:
                if self.stage_id.id != stage_sent.id:
                    self.write({'stage_id': stage_sent.id})

    def find_trigger_mailing_parent(self, new_campaign):
        updated_activities = []
        # clean scheduled date
        new_campaign.mailing_activities_ids.write({
            'schedule_date': False,
            'mailing_model_name': new_campaign.mailing_model_name,
            'mailing_model_id': new_campaign.mailing_model_id.id
        })

        for activity in new_campaign.mailing_activities_ids:

            if activity.id not in updated_activities:

                updating_activity = activity
                old_activity = self.mailing_activities_ids.filtered(
                    lambda m: m.name in updating_activity.name)
                if len(old_activity) > 1:
                    old_activity = old_activity[0]

                if activity.trigger == 'campaign_start':
                    wrong_activity_ids = new_campaign.mailing_activities_ids.filtered(
                        lambda m: m.trigger_mailing_id.id == old_activity.id)

                    for fix_activity in wrong_activity_ids:
                        fix_activity.trigger_mailing_id = updating_activity.id
                        updated_activities.append(fix_activity.id)
                elif activity.trigger_mailing_id.id < activity.id:
                    copy_trigger_mailing = self.env['mailing.mailing'].search([
                        ('name', 'ilike', activity.trigger_mailing_id.name), ('campaign_id', '=', new_campaign.id)
                    ], limit=1)
                    activity.trigger_mailing_id = copy_trigger_mailing.id
                    updated_activities.append(activity.id)
