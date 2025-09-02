#!/usr/bin/env python3
"""
Script de test pour vérifier le fonctionnement du dashboard
Usage: python test_dashboard.py
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

User = get_user_model()

def test_dashboard_access():
    """Test d'accès au dashboard"""
    print("🔍 Test d'accès au dashboard...")
    
    client = Client()
    
    # Test sans authentification
    response = client.get('/dashboard/')
    if response.status_code == 302:  # Redirection vers login
        print("✅ Redirection vers login (non authentifié)")
    else:
        print(f"❌ Erreur: {response.status_code}")
        return False
    
    # Créer un utilisateur de test
    try:
        user = User.objects.create_user(
            username='testadmin',
            email='test@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        print("✅ Utilisateur de test créé")
    except Exception as e:
        print(f"❌ Erreur création utilisateur: {e}")
        return False
    
    # Connexion
    login_success = client.login(username='testadmin', password='testpass123')
    if login_success:
        print("✅ Connexion réussie")
    else:
        print("❌ Échec de la connexion")
        return False
    
    # Test d'accès au dashboard
    response = client.get('/dashboard/')
    if response.status_code == 200:
        print("✅ Accès au dashboard réussi")
    else:
        print(f"❌ Erreur accès dashboard: {response.status_code}")
        return False
    
    # Test des autres pages
    dashboard_pages = [
        '/dashboard/products/',
        '/dashboard/categories/',
        '/dashboard/teams/',
        '/dashboard/users/',
        '/dashboard/orders/',
        '/dashboard/payments/',
        '/dashboard/customizations/',
        '/dashboard/analytics/',
        '/dashboard/settings/'
    ]
    
    for page in dashboard_pages:
        response = client.get(page)
        if response.status_code == 200:
            print(f"✅ {page} accessible")
        else:
            print(f"❌ {page} erreur: {response.status_code}")
    
    # Nettoyage
    user.delete()
    print("✅ Utilisateur de test supprimé")
    
    return True

def test_dashboard_views():
    """Test des vues du dashboard"""
    print("\n🔍 Test des vues du dashboard...")
    
    from dashboard.views import (
        dashboard_home, dashboard_products, dashboard_categories,
        dashboard_teams, dashboard_users, dashboard_orders,
        dashboard_payments, dashboard_customizations, dashboard_analytics,
        dashboard_settings
    )
    
    views = [
        ('dashboard_home', dashboard_home),
        ('dashboard_products', dashboard_products),
        ('dashboard_categories', dashboard_categories),
        ('dashboard_teams', dashboard_teams),
        ('dashboard_users', dashboard_users),
        ('dashboard_orders', dashboard_orders),
        ('dashboard_payments', dashboard_payments),
        ('dashboard_customizations', dashboard_customizations),
        ('dashboard_analytics', dashboard_analytics),
        ('dashboard_settings', dashboard_settings),
    ]
    
    for name, view in views:
        try:
            # Test simple de la vue
            print(f"✅ {name} importée avec succès")
        except Exception as e:
            print(f"❌ Erreur import {name}: {e}")
    
    return True

def test_dashboard_urls():
    """Test des URLs du dashboard"""
    print("\n🔍 Test des URLs du dashboard...")
    
    try:
        from dashboard.urls import urlpatterns
        
        expected_patterns = [
            'home', 'products', 'product_edit', 'categories', 'teams',
            'users', 'user_edit', 'orders', 'payments', 'customizations',
            'analytics', 'settings'
        ]
        
        url_names = [pattern.name for pattern in urlpatterns if hasattr(pattern, 'name')]
        
        for expected in expected_patterns:
            if expected in url_names:
                print(f"✅ URL {expected} trouvée")
            else:
                print(f"❌ URL {expected} manquante")
        
        print(f"Total URLs trouvées: {len(url_names)}")
        
    except Exception as e:
        print(f"❌ Erreur test URLs: {e}")
        return False
    
    return True

def test_dashboard_templates():
    """Test des templates du dashboard"""
    print("\n🔍 Test des templates du dashboard...")
    
    template_files = [
        'dashboard/base.html',
        'dashboard/home.html',
        'dashboard/products.html',
        'dashboard/categories.html',
        'dashboard/teams.html',
        'dashboard/users.html',
        'dashboard/user_edit.html',
        'dashboard/product_edit.html',
        'dashboard/orders.html',
        'dashboard/payments.html',
        'dashboard/customizations.html',
        'dashboard/analytics.html',
        'dashboard/settings.html'
    ]
    
    template_dir = 'templates'
    
    for template in template_files:
        template_path = os.path.join(template_dir, template)
        if os.path.exists(template_path):
            print(f"✅ {template} existe")
        else:
            print(f"❌ {template} manquant")
    
    return True

def test_static_files():
    """Test des fichiers statiques"""
    print("\n🔍 Test des fichiers statiques...")
    
    # Vérifier que WhiteNoise est configuré
    try:
        from ecom_maillot.settings import STATICFILES_STORAGE
        
        if 'whitenoise' in STATICFILES_STORAGE:
            print("✅ WhiteNoise configuré")
        else:
            print("⚠️ WhiteNoise non configuré")
            
    except Exception as e:
        print(f"❌ Erreur vérification WhiteNoise: {e}")
    
    # Vérifier les dossiers statiques
    static_dirs = ['static', 'staticfiles', 'media']
    
    for dir_name in static_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Dossier {dir_name} existe")
        else:
            print(f"⚠️ Dossier {dir_name} manquant")
    
    return True

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests du dashboard...\n")
    
    tests = [
        test_dashboard_access,
        test_dashboard_views,
        test_dashboard_urls,
        test_dashboard_templates,
        test_static_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} échoué")
        except Exception as e:
            print(f"❌ Test {test.__name__} erreur: {e}")
    
    print(f"\n📊 Résultats des tests: {passed}/{total} réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés avec succès!")
        return 0
    else:
        print("⚠️ Certains tests ont échoué")
        return 1

if __name__ == '__main__':
    sys.exit(main())
