# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import route



class TwilioWebhooks(http.Controller):

    @route(['/smsdev/input'], type='http', auth="none", methods=['GET', 'POST', 'OPTIONS'], cors="*", csrf=False)
    def smsdev_input(self,  **post):
        """
        Webhoock para receber mensagens do SmsDev
        https://painel.smsdev.com.br/integracao/callback
        {
            "from": "5562988887777", // Número que enviou o retorno
            "id": "123456789",       // ID do retorno
            "id_sent": "637849052",  // ID da mensagem enviada
            "message": "Teste de retorno", // Mensagem do retorno
            "refer": "XXXXXXX" // Referencia utiliza na mensagem de enviada
        }
        """
        if post.get('message', False) and post.get('from', False):
            pass



