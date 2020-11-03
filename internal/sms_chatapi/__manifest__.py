
{
    "name": "IAP ChatAPI for messages",
    "summary": "Send sms using ChatAPI IAP",
    "version": "13.0.1.0.1",
    "category": "SMS",
    'author': 'SUNNIT',
    'contributors': [
        'Hendrix Costa <hendrix@sunnit.com.br>',
        'Rafael Lima <lima@sunnit.com.br>',
    ],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": ["twilio"]},
    "depends": ["mass_mailing_base", "iap_alternative_provider"],
    "data": [
        "views/iap_account_view.xml",
    ],
    "demo": [],
    "qweb": [],
}


