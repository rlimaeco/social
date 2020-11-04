# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.mass_mailing_base.tools import helpers
from odoo.addons.phone_validation.tools import phone_validation

from odoo import models


class PhoneMixin(models.AbstractModel):
    _inherit = ['mail.thread.phone']

    def phone_get_sanitized_number(self, number_fname='mobile', force_format='E164'):

        sanitized = super(PhoneMixin, self).phone_get_sanitized_number(number_fname='mobile', force_format='E164')

        if sanitized:
            return sanitized

        country_fname = self._phone_get_country_field()
        number = self[number_fname]
        # Valida numero alternativo adicionando um 9 e caracteres de controle
        alternative_number = helpers.get_number_e164(number)
        sanitized = phone_validation.phone_sanitize_numbers_w_record([alternative_number], self, record_country_fname=country_fname, force_format=force_format)[alternative_number]['sanitized']
        if sanitized:
            return number

        return False
