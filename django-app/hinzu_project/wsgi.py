"""
WSGI config for hinzu_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from web_app.script import preprocess
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hinzu_project.settings')

def hinzu_go_2_work():
    print('preprocess starts')
    preprocess(settings)
    application = get_wsgi_application()
    return application

application = hinzu_go_2_work()
