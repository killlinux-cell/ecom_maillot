#!/usr/bin/env python
"""
Script de test pour vérifier le formatage des prix selon les standards ivoiriens
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

from core.templatetags.price_format import price_format, price_format_no_currency, price_format_compact

def test_price_formatting():
    """Test du formatage des prix"""
    print("🧪 Test du formatage des prix selon les standards ivoiriens")
    print("=" * 60)
    
    # Tests avec différents types de prix
    test_prices = [
        0,
        100,
        1000,
        15000,
        15000.50,
        15000.5,
        15000.99,
        100000,
        1000000,
        1000000.75,
        "15000.50",
        "100000",
        None,
        "",
        "invalid"
    ]
    
    print("📊 Tests du filtre price_format:")
    print("-" * 40)
    for price in test_prices:
        try:
            formatted = price_format(price)
            print(f"  {price} -> {formatted}")
        except Exception as e:
            print(f"  {price} -> ERREUR: {e}")
    
    print("\n📊 Tests du filtre price_format_no_currency:")
    print("-" * 40)
    for price in test_prices:
        try:
            formatted = price_format_no_currency(price)
            print(f"  {price} -> {formatted}")
        except Exception as e:
            print(f"  {price} -> ERREUR: {e}")
    
    print("\n📊 Tests du filtre price_format_compact:")
    print("-" * 40)
    for price in test_prices:
        try:
            formatted = price_format_compact(price)
            print(f"  {price} -> {formatted}")
        except Exception as e:
            print(f"  {price} -> ERREUR: {e}")
    
    print("\n✅ Tests terminés!")
    print("\n📋 Résumé des formats:")
    print("  • 15000.50 -> 15 000,50 FCFA (standard)")
    print("  • 15000.50 -> 15 000,50 (sans devise)")
    print("  • 15000 -> 15 000 FCFA (compact)")
    print("  • 15000.50 -> 15 000,50 FCFA (compact)")

if __name__ == '__main__':
    test_price_formatting()
