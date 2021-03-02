# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mass_mailing_sms.controllers.main import MailingSMSController

from odoo.http import request


class MailingController(MailingSMSController):

    def _check_trace(self, mailing_id, trace_code):
        try:
            mailing = request.env['mailing.mailing'].sudo().search([('id', '=', mailing_id)])
        except:
            mailing = False
        if not mailing:
            return {'error': 'mailing_error'}

        if mailing.mailing_type == 'whatsapp':
            trace_type = mailing.mailing_type
        else:
            trace_type = 'sms'

        trace = request.env['mailing.trace'].sudo().search([
            ('trace_type', '=', trace_type),
            ('sms_code', '=', trace_code),
            ('mass_mailing_id', '=', mailing.id)
        ])
        if not trace:
            return {'error': 'trace_error'}
        return {'trace': trace}
