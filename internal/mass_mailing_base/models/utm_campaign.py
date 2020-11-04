# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    mailing_whatsapp_ids = fields.One2many(
        comodel_name='mailing.mailing',
        inverse_name='campaign_id',
        domain=[('mailing_type', '=', 'whatsapp')],
        string='Mass Whatsapp',
    )

    mailing_whatsapp_count = fields.Integer(
        string='Number of Mass Whatsapp',
        compute="_compute_mailing_whatsapp_count",
    )

    @api.depends('mailing_whatsapp_ids')
    def _compute_mailing_whatsapp_count(self):
        for campaign in self:
            campaign.mailing_whatsapp_count = len(campaign.mailing_whatsapp_ids)

    def action_create_mass_whatsapp(self):
        action = self.env.ref('mass_mailing.action_create_mass_mailings_from_campaign').read()[0]
        action['context'] = {
            'default_campaign_id': self.id,
            'default_mailing_type': 'whatsapp',
            'search_default_assigned_to_me': 1,
            'search_default_campaign_id': self.id,
            'default_user_id': self.env.user.id,
            'mailing_sms': True,
        }
        return action

    def action_redirect_to_mailing_whatsapp(self):
        action = self.env.ref('mass_mailing.action_view_mass_mailings_from_campaign').read()[0]
        action['context'] = {
            'default_campaign_id': self.id,
            'default_mailing_type': 'whatsapp',
            'search_default_assigned_to_me': 1,
            'search_default_campaign_id': self.id,
            'default_user_id': self.env.user.id,
            'mailing_sms': True,
        }
        action['domain'] = [('mailing_type', '=', 'whatsapp')]
        return action

