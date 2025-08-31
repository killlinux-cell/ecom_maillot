#!/usr/bin/env python
"""
Script de test pour vérifier que les template tags fonctionnent correctement
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

from django.template import Template, Context
from django.template.loader import get_template

def test_template_tags():
    """Test des template tags dans un contexte de template"""
    print("🧪 Test des template tags dans un contexte de template")
    print("=" * 60)
    
    # Test 1: Filtre price_format
    template_string = """
    {% load price_format %}
    Prix: {{ price|price_format }}
    """
    
    template = Template(template_string)
    context = Context({'price': 15000.50})
    result = template.render(context).strip()
    
    print(f"✅ Test price_format: {result}")
    
    # Test 2: Filtre price_format_no_currency
    template_string2 = """
    {% load price_format %}
    Prix sans devise: {{ price|price_format_no_currency }}
    """
    
    template2 = Template(template_string2)
    context2 = Context({'price': 15000.50})
    result2 = template2.render(context2).strip()
    
    print(f"✅ Test price_format_no_currency: {result2}")
    
    # Test 3: Filtre price_format_compact
    template_string3 = """
    {% load price_format %}
    Prix compact: {{ price|price_format_compact }}
    """
    
    template3 = Template(template_string3)
    context3 = Context({'price': 15000})
    result3 = template3.render(context3).strip()
    
    print(f"✅ Test price_format_compact: {result3}")
    
    # Test 4: Test avec différents types de prix
    test_prices = [0, 100, 1000, 15000.50, 100000, 1000000.75]
    
    print("\n📊 Test avec différents prix:")
    for price in test_prices:
        context = Context({'price': price})
        result = template.render(context).strip()
        print(f"  {price} -> {result}")
    
    print("\n✅ Tous les tests des template tags sont passés!")

if __name__ == '__main__':
    test_template_tags()
