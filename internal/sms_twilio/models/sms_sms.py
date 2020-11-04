# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mass_mailing_base.tools import helpers

from odoo import api, fields, models


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    message_id = fields.Char(string="SMS ID")

    TWILIO_TO_SMS_STATE = {
        'queued': 'sent',
        'sent': 'sent',
        'undelivered': 'sms_number_format',
        'failed': 'sms_server'
    }

    def _postprocess_iap_sent_sms(self, iap_results, failure_reason=None, delete_all=False):
        try:

            res = super(SmsSms, self)._postprocess_iap_sent_sms(iap_results, failure_reason=failure_reason, delete_all=delete_all)
            if res is None:

                all_sms_ids = [item['res_id'] for item in iap_results]
                if any(sms.mailing_id for sms in self.env['sms.sms'].sudo().browse(all_sms_ids)):
                    for state in self.TWILIO_TO_SMS_STATE.keys():
                        sms_ids = [item['res_id'] for item in iap_results if item['state'] == state]
                        traces = self.env['mailing.trace'].sudo().search([
                            ('sms_sms_id_int', 'in', sms_ids)
                        ])
                        if traces and state in ['sent', 'queued']:
                            traces.write({'sent': fields.Datetime.now(), 'exception': False})
                        elif traces:
                            traces.set_failed(failure_type=self.TWILIO_TO_SMS_STATE[state])

        except Exception as e:
            print(str(e))
            return True

        return res
