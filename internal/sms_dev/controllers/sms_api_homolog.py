# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# Copyright (C) 2021 - Rafael Lima <rafaelslima.py@gmail.com>
# Copyright (C) 2021 - Hendrix Costa <hendrixcosta@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from random import random

from odoo import http
from odoo.http import route


class SmsDEVWebhooksHomolog(http.Controller):

    @route(['/smsdev/homolog'], type='http', auth="public", methods=['GET', 'POST', 'OPTIONS'], cors="*", csrf=False)
    def smsdev_input_homolog(self,  **post):
        """ Validacao da API do SMSDEV """
        error = ""

        if not post.get("key"):
            error += "Faltando Chave de autenticação de conta. "

        if not post.get("type"):
            error += "Tipo de serviço incorreto: Tipo de serviço: 9-Sms. "

        if not post.get("number"):
            error += "Faltando Número destinatário. "
            if len(post.get("number")) not in [13, 11]:
                error += "Número INválido. "

        if not post.get("key"):
            error += "Faltando Texto da mensagem. "

        if not error:
            response = {
                "situacao" : "OK",
                "codigo" : "1",
                "id" : str(random())[-9:],
                "descricao" : "MENSAGEM NA FILA"
            }
        else:
            response = {"error": error}

        return json.dumps(response)
