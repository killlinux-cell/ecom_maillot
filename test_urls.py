#!/usr/bin/env python
"""
Script de test pour vérifier la résolution des URLs du dashboard
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

def test_dashboard_urls():
    """Teste toutes les URLs du dashboard"""
    
    # URLs à tester
    urls_to_test = [
        'dashboard:home',
        'dashboard:products',
        'dashboard:categories',
        'dashboard:teams',
        'dashboard:users',
        'dashboard:orders',
        'dashboard:payments',
        'dashboard:customizations',
        'dashboard:analytics',
        'dashboard:settings',
    ]
    
    print("🔍 Test des URLs du Dashboard")
    print("=" * 50)
    
    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✅ {url_name:25} -> {url}")
        except NoReverseMatch as e:
            print(f"❌ {url_name:25} -> ERREUR: {e}")
        except Exception as e:
            print(f"⚠️  {url_name:25} -> ERREUR INATTENDUE: {e}")
    
    print("=" * 50)
    print("Test terminé!")

if __name__ == '__main__':
    test_dashboard_urls()
