# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo.addons.phone_validation.tools import phone_validation


def valid_alternative_9number(info):
    """Validar um numero alternativo adicionando um numero 9"""
    if not info.get("number", False):
        return False

    simple_number = re.sub('[^0-9]', '', info.get("number"))

    # 92415585
    if len(simple_number) == 8:
        alternative_number = "+9{}".format(simple_number)

    # 9 92415585
    if len(simple_number) == 9:
        alternative_number = "+{}".format(simple_number)

    # 35 9241 5585
    elif len(simple_number) == 10:
        alternative_number = "+55{}9{}".format(
            simple_number[:2], simple_number[-8:])

    # 35 9 9241 5585
    elif len(simple_number) == 11:
        alternative_number = "+55{}".format(simple_number)

    # 55 35 9241 5585
    elif len(simple_number) == 12:
        alternative_number = "+{}9{}".format(
            simple_number[:4], simple_number[-8:])

    # 55 35 9 9241 5585
    elif len(simple_number) == 13:
        alternative_number = "+{}".format(simple_number)

    else:
        alternative_number = simple_number

    valid_number = phone_validation.phone_sanitize_numbers_w_record(
        [alternative_number], info.get("partner"))

    if valid_number.get(alternative_number).get("sanitized"):
        return valid_number.get(alternative_number).get("sanitized")
    return False

def sanitize_mobile_cut(number):
    """Remover caracteres de controle"""
    return re.sub('[^0-9]', '', number)[-8:] if number else ""

def sanitize_mobile_full(number):
    """Remover caracteres de controle"""
    return re.sub('[^0-9]', '', number) if number else ""

def sanitize_mobile(number):
    """Adicionar caracteres de controle"""
    return "+{}".format(re.sub('[^0-9]', '', number)) if number else ""

def get_record_from_number(model, number):
    """Buscar uma lead existente baseado no numero"""
    all_records_ids = model.sudo().search([("mobile", "!=", False)])
    record_id = all_records_ids.filtered(
        lambda x: sanitize_mobile_cut(x.mobile) == number)
    return record_id[0] if record_id else False
