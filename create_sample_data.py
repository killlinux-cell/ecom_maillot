#!/usr/bin/env python
"""
Script pour créer des données de test pour l'e-commerce de maillots de football
"""

import os
import sys
import django
from decimal import Decimal
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

from products.models import Category, Team, Product, ProductImage
from django.contrib.auth.models import User
from django.core.files.base import ContentFile


def create_categories():
    """Créer les catégories de produits"""
    categories_data = [
        {
            'name': 'Maillots Domicile',
            'description': 'Maillots officiels de domicile des équipes de football'
        },
        {
            'name': 'Maillots Extérieur',
            'description': 'Maillots officiels d\'extérieur des équipes de football'
        },
        {
            'name': 'Maillots Third',
            'description': 'Maillots officiels third des équipes de football'
        },
        {
            'name': 'Maillots Rétro',
            'description': 'Maillots rétro et vintage des équipes de football'
        },
        {
            'name': 'Maillots Équipes Nationales',
            'description': 'Maillots officiels des équipes nationales'
        }
    ]
    
    categories = []
    for data in categories_data:
        category, created = Category.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        categories.append(category)
        if created:
            print(f"✓ Catégorie créée: {category.name}")
        else:
            print(f"⚠ Catégorie existante: {category.name}")
    
    return categories


def create_teams():
    """Créer les équipes de football"""
    teams_data = [
        # Équipes européennes
        {'name': 'Real Madrid', 'country': 'Espagne', 'league': 'La Liga'},
        {'name': 'Barcelona', 'country': 'Espagne', 'league': 'La Liga'},
        {'name': 'Manchester United', 'country': 'Angleterre', 'league': 'Premier League'},
        {'name': 'Manchester City', 'country': 'Angleterre', 'league': 'Premier League'},
        {'name': 'Liverpool', 'country': 'Angleterre', 'league': 'Premier League'},
        {'name': 'Chelsea', 'country': 'Angleterre', 'league': 'Premier League'},
        {'name': 'Arsenal', 'country': 'Angleterre', 'league': 'Premier League'},
        {'name': 'Bayern Munich', 'country': 'Allemagne', 'league': 'Bundesliga'},
        {'name': 'Borussia Dortmund', 'country': 'Allemagne', 'league': 'Bundesliga'},
        {'name': 'Paris Saint-Germain', 'country': 'France', 'league': 'Ligue 1'},
        {'name': 'Juventus', 'country': 'Italie', 'league': 'Serie A'},
        {'name': 'AC Milan', 'country': 'Italie', 'league': 'Serie A'},
        {'name': 'Inter Milan', 'country': 'Italie', 'league': 'Serie A'},
        
        # Équipes nationales
        {'name': 'Équipe de France', 'country': 'France', 'league': 'International'},
        {'name': 'Équipe d\'Espagne', 'country': 'Espagne', 'league': 'International'},
        {'name': 'Équipe d\'Allemagne', 'country': 'Allemagne', 'league': 'International'},
        {'name': 'Équipe d\'Angleterre', 'country': 'Angleterre', 'league': 'International'},
        {'name': 'Équipe du Brésil', 'country': 'Brésil', 'league': 'International'},
        {'name': 'Équipe d\'Argentine', 'country': 'Argentine', 'league': 'International'},
        {'name': 'Équipe du Portugal', 'country': 'Portugal', 'league': 'International'},
        {'name': 'Équipe de Côte d\'Ivoire', 'country': 'Côte d\'Ivoire', 'league': 'International'},
    ]
    
    teams = []
    for data in teams_data:
        team, created = Team.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        teams.append(team)
        if created:
            print(f"✓ Équipe créée: {team.name}")
        else:
            print(f"⚠ Équipe existante: {team.name}")
    
    return teams


def create_products(categories, teams):
    """Créer les produits (maillots)"""
    products_data = []
    
    # Générer des produits pour chaque équipe
    for team in teams:
        for category in categories:
            # Prix de base selon la catégorie
            base_price = 15000 if 'Nationales' in category.name else 12000
            
            # Créer plusieurs variantes
            for variant in range(1, 4):
                product_data = {
                    'name': f"Maillot {team.name} {category.name} {variant}",
                    'category': category,
                    'team': team,
                    'description': f"Maillot officiel {category.name.lower()} de {team.name}. Matériau de haute qualité, design authentique et confortable.",
                    'price': Decimal(base_price + random.randint(-2000, 2000)),
                    'available_sizes': ['S', 'M', 'L', 'XL', 'XXL'],
                    'stock_quantity': random.randint(10, 50),
                    'is_featured': random.choice([True, False]),
                    'is_active': True
                }
                
                # Ajouter des promotions aléatoires
                if random.random() < 0.3:  # 30% de chance d'être en promotion
                    product_data['sale_price'] = product_data['price'] * Decimal('0.8')  # 20% de réduction
                
                products_data.append(product_data)
    
    products = []
    for data in products_data:
        product, created = Product.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        products.append(product)
        if created:
            print(f"✓ Produit créé: {product.name}")
        else:
            print(f"⚠ Produit existant: {product.name}")
    
    return products


def create_superuser():
    """Créer un superutilisateur si il n'existe pas"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@maillots-football.ci',
            password='admin123'
        )
        print("✓ Superutilisateur créé: admin/admin123")
    else:
        print("⚠ Superutilisateur existant")


def main():
    """Fonction principale"""
    print("🚀 Création des données de test pour l'e-commerce de maillots de football")
    print("=" * 70)
    
    # Créer le superutilisateur
    create_superuser()
    print()
    
    # Créer les catégories
    print("📂 Création des catégories...")
    categories = create_categories()
    print()
    
    # Créer les équipes
    print("⚽ Création des équipes...")
    teams = create_teams()
    print()
    
    # Créer les produits
    print("🛍️ Création des produits...")
    products = create_products(categories, teams)
    print()
    
    print("=" * 70)
    print("✅ Données de test créées avec succès !")
    print(f"📊 Statistiques:")
    print(f"   - {len(categories)} catégories")
    print(f"   - {len(teams)} équipes")
    print(f"   - {len(products)} produits")
    print()
    print("🔗 Accès:")
    print(f"   - Site web: http://localhost:8000")
    print(f"   - Admin: http://localhost:8000/admin (admin/admin123)")
    print()
    print("🎯 Prochaines étapes:")
    print("   1. Lancer le serveur: python manage.py runserver")
    print("   2. Ajouter des images aux produits via l'admin")
    print("   3. Configurer PayDunya pour les paiements")


if __name__ == '__main__':
    main()
