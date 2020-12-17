{
    'name': 'Mass Mailing Base',
    'summary': 'Base for mass mailing sms messages',
    'description': '',
    'version': '13.0.1.0.5',
    'author': 'SUNNIT',
    'category': 'Marketing/Email Marketing',
    'contributors': [
        'Hendrix Costa <hendrix@sunnit.com.br>',
        'Rafael Lima <lima@sunnit.com.br>',
    ],
    'depends': [
        'mass_mailing_sms', 'phone_validation','utm', 'mass_mailing_sale'
    ],
    'data': [
        'wizard/sms_composer_views.xml',
        'views/sms_sms_views.xml',
        'views/utm_campaign_views.xml',
        'views/mailing_mailing_view.xml',
        'views/iap_account_view.xml',
        'views/mailing_trace_views.xml',
        'views/mailing_contact_views.xml',
        'data/utm_data.xml',
    ],
    'demo': [
    ],
    'application': True,
}
