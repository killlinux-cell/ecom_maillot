"""
WSGI config for ecom_maillot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')

application = get_wsgi_application()

# Configuration WhiteNoise pour servir les fichiers statiques ET media en production
from whitenoise import WhiteNoise
application = WhiteNoise(application, root='staticfiles/')

# Ajouter le dossier media pour servir les images des produits
media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
application.add_files(media_root, prefix='media/')
