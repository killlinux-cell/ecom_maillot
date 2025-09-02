#!/usr/bin/env python3
"""
Script de test simple pour le dashboard
Usage: python test_dashboard_simple.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

def test_dashboard_urls():
    """Test des URLs du dashboard"""
    print("🔍 Test des URLs du dashboard...")
    
    try:
        from dashboard.urls import urlpatterns
        
        print(f"✅ URLs trouvées: {len(urlpatterns)}")
        for pattern in urlpatterns:
            if hasattr(pattern, 'name'):
                print(f"  - {pattern.name}: {pattern.pattern}")
        
    except Exception as e:
        print(f"❌ Erreur URLs: {e}")
        return False
    
    return True

def test_dashboard_views():
    """Test des vues du dashboard"""
    print("\n🔍 Test des vues du dashboard...")
    
    try:
        from dashboard.views import dashboard_home
        print("✅ Vue dashboard_home importée")
        
        # Test de la vue sans requête
        print("✅ Import des vues réussi")
        
    except Exception as e:
        print(f"❌ Erreur vues: {e}")
        return False
    
    return True

def test_models():
    """Test des modèles utilisés"""
    print("\n🔍 Test des modèles...")
    
    try:
        from orders.models import Order, OrderItem
        from products.models import Product
        from django.contrib.auth.models import User
        
        print("✅ Modèles importés avec succès")
        
        # Vérifier les champs
        order_fields = [f.name for f in Order._meta.fields]
        orderitem_fields = [f.name for f in OrderItem._meta.fields]
        product_fields = [f.name for f in Product._meta.fields]
        
        print(f"✅ Champs Order: {len(order_fields)}")
        print(f"✅ Champs OrderItem: {len(orderitem_fields)}")
        print(f"✅ Champs Product: {len(product_fields)}")
        
        # Vérifier le champ product_name
        if 'product_name' in orderitem_fields:
            print("✅ Champ product_name trouvé dans OrderItem")
        else:
            print("❌ Champ product_name manquant dans OrderItem")
            return False
        
    except Exception as e:
        print(f"❌ Erreur modèles: {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("🚀 Test simple du dashboard...\n")
    
    tests = [
        test_dashboard_urls,
        test_dashboard_views,
        test_models
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
    
    print(f"\n📊 Résultats: {passed}/{total} réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés!")
        return 0
    else:
        print("⚠️ Certains tests ont échoué")
        return 1

if __name__ == '__main__':
    sys.exit(main())
