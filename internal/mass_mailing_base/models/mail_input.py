# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MailInput(models.Model):
    _name = 'mail.input'
    _inherit = ['mail.thread']
    _description = "Add feature for receive email and store in partner"

    partner_id = fields.Many2one(
        string='Related Partner',
        comodel_name='res.partner',
        required=True,
        ondelete='cascade',
        index=True,
    )

    def create_mail_message(self, partner, body):
        if partner:
            message = self.env['mail.message'].create({
                'subject': 'Message from Email',
                'body': body,
                'author_id': partner.id,
                'res_id': partner.id,
                'email_from': partner.email or False,
                'message_type': 'email',
                'model': 'res.partner'
            })
            return message or False

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        email_from_str = msg_dict.get('email_from', False)
        if email_from_str:
            try:
                name_from = re.findall(r'\"(.+?)\"', email_from_str)[0]
                email_from = re.findall('\S+@\S+', email_from_str)[0][1:-1]
            except IndexError:
                return False
            except ValidationError:
                return False
            else:
                partner = self.env['res.partner'].search([('email', '=', email_from)], limit=1)
                if not partner:
                    partner = self.env['res.partner'].create({
                        'name': name_from,
                        'email': email_from
                    })

                self.create_mail_message(partner, msg_dict.get('body'))

                if custom_values is None:
                    custom_values = {'partner_id': partner.id}

                return super(MailInput, self).message_new(msg_dict, custom_values)
