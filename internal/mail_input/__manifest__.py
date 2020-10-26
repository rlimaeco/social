
{
    "name": "Mail Input",
    "summary": "Receive emails directly in partner's messages",
    "version": "13.0.1.0.2",
    "category": "Contacts",
    'author': 'SUNNIT',
    'contributors': [
        'Rafael Lima <lima@sunnit.com.br>',
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


