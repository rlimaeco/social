{
    'name': 'Mass Mailing Base 14',
    'summary': 'Base for mass mailing sms messages 14',
    'description': '',
    'version': '14.0.0.0.1',
    'author': 'SUNNIT',
    'category': 'Marketing/Email Marketing',
    'contributors': [
        'Hendrix Costa <hendrix@sunnit.com.br>',
        'Rafael Lima <rafaelslima.py@gmail.com>',
    ],
    'depends': [
        'mass_mailing_sms', 'phone_validation', 'utm', 'iap_alternative_provider'
    ],
    'data': [
        'wizard/sms_composer_views.xml',
        'views/sms_sms_views.xml',
        'views/utm_campaign_views.xml',
        'views/mailing_mailing_view.xml',
        'views/iap_account_view.xml',
        'views/mailing_trace_views.xml',
        'data/utm_data.xml',
    ],
    'demo': [
    ],
    'application': True,
    "installable": True,

}
