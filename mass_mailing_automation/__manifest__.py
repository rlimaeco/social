{
    'name': 'Mass Mailing Automation',
    'summary': 'Module for Automation mass mailing',
    'description': 'Module for Automation mass mailing',
    'version': '14.0.0.0.1',
    'author': 'SUNNIT',
    'category': 'Marketing/Email Marketing',
    'contributors': [
        'Rafael Lima <lima@sunnit.com.br>',
        'Hendrix Costa <hendrix@sunnit.com.br>',
    ],
    'depends': [
        'mass_mailing_base',
    ],
    'data': [
        'data/utm_data.xml',
        'views/utm_campaign_views.xml',
        'views/mail_template_views.xml',
        'views/mailing_mailing_view.xml',
        'views/base_menu.xml',
        'wizard/utm_campaign_schedule_date_views.xml',
    ],
    'demo': [
    ],
    'application': True,
}
