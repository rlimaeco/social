{
    'name': 'Mass Mailing Base',
    'summary': 'Base for mass mailing sms messages',
    'description': '',
    'version': '14.0.1.1.7',
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
        'data/utm_data.xml',
        'views/sms_sms_views.xml',
        'views/utm_campaign_views.xml',
        'views/mailing_mailing_view.xml',
        'views/iap_account_view.xml',
        'views/mailing_trace_views.xml',
        'views/mailing_contact_views.xml',
        'wizard/sms_composer_views.xml',
        'wizard/mailing_whatsapp_test_views.xml',
    ],
    'demo': [
    ],
    'application': True,
    "installable": True,

}
