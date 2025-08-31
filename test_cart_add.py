#!/usr/bin/env python
"""
Script de test pour vérifier que cart_add fonctionne correctement
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

from products.models import Product, JerseyCustomization
from cart.models import Cart, CartItem
from products.models import CartItemCustomization
from django.contrib.auth.models import User
from decimal import Decimal

def test_cart_add():
    """Test de l'ajout au panier avec personnalisations"""
    print("🧪 Test de cart_add avec personnalisations...")
    
    # 1. Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='test_cart_user',
        defaults={
            'email': 'test_cart@example.com',
            'first_name': 'Test',
            'last_name': 'Cart'
        }
    )
    print(f"1. Utilisateur: {user.username}")
    
    # 2. Récupérer un produit
    product = Product.objects.first()
    if not product:
        print("❌ Aucun produit trouvé")
        return
    print(f"2. Produit: {product.name}")
    
    # 3. Créer un panier
    cart, created = Cart.objects.get_or_create(user=user)
    print(f"3. Panier créé: {cart}")
    
    # 4. Ajouter un article au panier
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size='M',
        defaults={'quantity': 1}
    )
    print(f"4. Article ajouté: {cart_item}")
    
    # 5. Tester les méthodes de personnalisation
    print("\n5. Test des méthodes de personnalisation:")
    
    # Test nom/numéro
    name_custom = JerseyCustomization.get_or_create_name_customization()
    print(f"   ✅ Nom/Numéro: {name_custom}")
    
    # Test badge
    badge_custom = JerseyCustomization.get_or_create_badge_customization('champions')
    print(f"   ✅ Badge Champions: {badge_custom}")
    
    # 6. Ajouter des personnalisations
    print("\n6. Ajout de personnalisations:")
    
    # Personnalisation nom
    name_cart_custom = CartItemCustomization.objects.create(
        cart_item=cart_item,
        customization=name_custom,
        custom_text="MESSI 10",
        price=Decimal('4000.00')
    )
    print(f"   ✅ Nom ajouté: {name_cart_custom}")
    
    # Personnalisation badge
    badge_cart_custom = CartItemCustomization.objects.create(
        cart_item=cart_item,
        customization=badge_custom,
        price=Decimal('500.00')
    )
    print(f"   ✅ Badge ajouté: {badge_cart_custom}")
    
    # 7. Vérifier les prix
    print(f"\n7. Calcul des prix:")
    print(f"   - Prix de base: {cart_item.base_price} FCFA")
    print(f"   - Prix personnalisations: {cart_item.customization_price} FCFA")
    print(f"   - Prix total: {cart_item.total_price} FCFA")
    
    # 8. Vérifier qu'il n'y a pas de doublons
    print(f"\n8. Vérification des doublons:")
    name_customs = JerseyCustomization.objects.filter(customization_type='name')
    badge_customs = JerseyCustomization.objects.filter(customization_type='badge', badge_type='champions')
    
    print(f"   - Personnalisations nom/numéro: {name_customs.count()}")
    print(f"   - Personnalisations badge champions: {badge_customs.count()}")
    
    if name_customs.count() == 1 and badge_customs.count() == 1:
        print("   ✅ Aucun doublon détecté!")
    else:
        print("   ❌ Doublons détectés!")
    
    print(f"\n✅ Test terminé avec succès!")

if __name__ == '__main__':
    test_cart_add()
