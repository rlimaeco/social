# -*- coding: utf-8 -*-
# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class UtmCampaignScheduleDate(models.TransientModel):
    _name = 'utm.campaign.schedule.date'
    _description = 'UTM Campaign Scheduling'

    schedule_date = fields.Datetime(string='Scheduled for')
    utm_campaign_id = fields.Many2one('utm.campaign', required=True, ondelete='cascade')

    @api.constrains('schedule_date')
    def _check_schedule_date(self):
        for scheduler in self:
            if scheduler.schedule_date < fields.Datetime.now():
                raise ValidationError(_('Please select a date equal/or greater than the current date.'))

    def set_schedule_date(self):
        start_activity_ids = self.utm_campaign_id.mailing_activities_ids.filtered(lambda m: m.trigger == 'campaign_start')
        for activity in start_activity_ids:
            activity.write({'schedule_date': self.schedule_date, 'state': 'in_queue'})
            self.utm_campaign_id.set_children_activity_states(activity, schedule=self.schedule_date)
