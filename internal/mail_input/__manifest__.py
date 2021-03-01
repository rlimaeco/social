
{
    "name": "Mail Input",
    "summary": "Receive e-mails in leads",
    "version": "14.0.0.0.1",
    "category": "Contacts",
    'author': 'SUNNIT',
    'contributors': [
        'Rafael Lima <lima@sunnit.com.br>',
        'Hendrix Costa <hendrixcosta@gmail.com>',
    ],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mail", "sunnit_crm"],
    "data": [
        'security/ir.model.access.csv',
        "views/mail_input_view.xml"
    ],
    "demo": [],
    "qweb": [],
}


