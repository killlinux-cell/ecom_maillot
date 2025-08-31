#!/usr/bin/env python
"""
Script pour créer les options de personnalisation des maillots
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

from products.models import JerseyCustomization

def create_customization_options():
    """Créer les options de personnalisation des maillots"""
    
    # Supprimer les options existantes
    JerseyCustomization.objects.all().delete()
    
    # Options de nom/numéro (500 FCFA par caractère)
    name_options = [
        {
            'name': 'Nom et Numéro',
            'customization_type': 'name',
            'price': 500.00,
            'description': 'Ajoutez votre nom et numéro sur le maillot. Prix: 500 FCFA par caractère.'
        }
    ]
    
    # Options de badges (500 FCFA chacun)
    badge_options = [
        {
            'name': 'Badge Liga',
            'customization_type': 'badge',
            'badge_type': 'liga',
            'price': 500.00,
            'description': 'Badge officiel de la Liga espagnole'
        },
        {
            'name': 'Badge UEFA',
            'customization_type': 'badge',
            'badge_type': 'uefa',
            'price': 500.00,
            'description': 'Badge officiel UEFA'
        },
        {
            'name': 'Badge Champions League',
            'customization_type': 'badge',
            'badge_type': 'champions',
            'price': 500.00,
            'description': 'Badge officiel de la Champions League'
        },
        {
            'name': 'Badge Europa League',
            'customization_type': 'badge',
            'badge_type': 'europa',
            'price': 500.00,
            'description': 'Badge officiel de l\'Europa League'
        },
        {
            'name': 'Badge Premier League',
            'customization_type': 'badge',
            'badge_type': 'premier',
            'price': 500.00,
            'description': 'Badge officiel de la Premier League'
        },
        {
            'name': 'Badge Bundesliga',
            'customization_type': 'badge',
            'badge_type': 'bundesliga',
            'price': 500.00,
            'description': 'Badge officiel de la Bundesliga'
        },
        {
            'name': 'Badge Serie A',
            'customization_type': 'badge',
            'badge_type': 'serie_a',
            'price': 500.00,
            'description': 'Badge officiel de la Serie A'
        },
        {
            'name': 'Badge Ligue 1',
            'customization_type': 'badge',
            'badge_type': 'ligue_1',
            'price': 500.00,
            'description': 'Badge officiel de la Ligue 1'
        }
    ]
    
    # Créer les options de nom/numéro
    for option in name_options:
        JerseyCustomization.objects.create(**option)
        print(f"✓ Créé: {option['name']} - {option['price']} FCFA")
    
    # Créer les options de badges
    for option in badge_options:
        JerseyCustomization.objects.create(**option)
        print(f"✓ Créé: {option['name']} - {option['price']} FCFA")
    
    print(f"\n✅ {len(name_options) + len(badge_options)} options de personnalisation créées avec succès !")
    print("\nOptions disponibles:")
    print("- Nom/Numéro: 500 FCFA par caractère")
    print("- Badges: 500 FCFA chacun")
    print("- Chiffres: 500 FCFA par chiffre")

if __name__ == '__main__':
    create_customization_options()
