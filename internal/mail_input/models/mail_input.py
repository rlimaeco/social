# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models


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
    subject = fields.Char('Subject')
    email_from = fields.Char('From')

    def name_get(self):
        result = []
        for rec in self:
            if len(rec.subject) > 30:
                name = f'{rec.subject[:30]}...'
            else:
                name = rec.subject

            result.append((rec.id, name))
        return result

    def create_mail_message(self, partner, msg_dict):
        fetchmail_server_ids = self.env['fetchmail.server'].search([])
        fetchmail_server = False
        for server in fetchmail_server_ids:
            if server.object_id.model == 'mail.input':
                fetchmail_server = server

        if partner:
            message = self.env['mail.message'].create({
                'subject': msg_dict.get('subject'),
                'body': msg_dict.get('body'),
                'author_id': partner.id,
                'res_id': partner.id,
                'email_from': partner.email or False,
                'message_type': 'email',
                'model': 'res.partner'
            })
            mail = self.env["mail.mail"].create(
                {
                    "mail_message_id": message.id,
                    "fetchmail_server_id": fetchmail_server.id,
                    "subject": msg_dict.get('subject'),
                    "email_from": partner.email or False,
                    "email_to": msg_dict.get('to'),
                    "body_html": msg_dict.get('body'),
                    "state": 'received'
                }
            )

            return message,mail or False

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        email_from_str = msg_dict.get('email_from', False)
        if email_from_str:
            try:
                name_from = re.findall(r'\"(.+?)\"', email_from_str)[0]
                email_from = re.findall('\S+@\S+', email_from_str)[0][1:-1]
            except Exception:
                return False
            else:
                partner = self.env['res.partner'].search([('email', '=', email_from)], limit=1)
                if not partner:
                    partner = self.env['res.partner'].create({
                        'name': name_from,
                        'email': email_from
                    })

                self.create_mail_message(partner, msg_dict)

                if custom_values is None:
                    custom_values = {
                        'partner_id': partner.id,
                        'subject': msg_dict.get('subject'),
                        'email_from': email_from,
                    }

                return super(MailInput, self).message_new(msg_dict, custom_values)
