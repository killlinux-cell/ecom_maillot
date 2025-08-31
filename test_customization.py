#!/usr/bin/env python
"""
Script de test pour vérifier le fonctionnement des personnalisations
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

from django.contrib.auth.models import User
from products.models import Product, JerseyCustomization
from cart.models import Cart, CartItem
from products.models import CartItemCustomization
from orders.models import Order, OrderItem, OrderItemCustomization
from decimal import Decimal

def test_customizations():
    """Test du système de personnalisations"""
    print("=== Test du système de personnalisations ===\n")
    
    # 1. Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    print(f"1. Utilisateur de test: {user.username}")
    
    # 2. Récupérer un produit
    product = Product.objects.first()
    if not product:
        print("❌ Aucun produit trouvé dans la base de données")
        return
    print(f"2. Produit sélectionné: {product.name}")
    
    # 3. Créer des personnalisations de test
    name_customization, created = JerseyCustomization.objects.get_or_create(
        name="Nom/Numéro personnalisé",
        customization_type="name",
        defaults={'price': Decimal('500')}
    )
    
    badge_customization, created = JerseyCustomization.objects.get_or_create(
        name="Badge Champions League",
        customization_type="badge",
        badge_type="champions",
        defaults={'price': Decimal('1000')}
    )
    
    print(f"3. Personnalisations créées:")
    print(f"   - {name_customization.name}: {name_customization.price} FCFA")
    print(f"   - {badge_customization.name}: {badge_customization.price} FCFA")
    
    # 4. Créer un panier
    cart, created = Cart.objects.get_or_create(user=user)
    print(f"4. Panier créé pour {user.username}")
    
    # 5. Ajouter un article au panier
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size='M',
        defaults={'quantity': 1}
    )
    print(f"5. Article ajouté au panier: {cart_item}")
    
    # 6. Ajouter des personnalisations à l'article
    # Personnalisation nom/numéro
    name_cart_custom = CartItemCustomization.objects.create(
        cart_item=cart_item,
        customization=name_customization,
        custom_text="MESSI 10",
        quantity=1
    )
    
    # Personnalisation badge
    badge_cart_custom = CartItemCustomization.objects.create(
        cart_item=cart_item,
        customization=badge_customization,
        quantity=1
    )
    
    print(f"6. Personnalisations ajoutées:")
    print(f"   - Nom: '{name_cart_custom.custom_text}' (Prix: {name_cart_custom.price} FCFA)")
    print(f"   - Badge: {badge_cart_custom.customization.name} (Prix: {badge_cart_custom.price} FCFA)")
    
    # 7. Vérifier les prix
    print(f"\n7. Calcul des prix:")
    print(f"   - Prix de base du produit: {cart_item.base_price} FCFA")
    print(f"   - Prix des personnalisations: {cart_item.customization_price} FCFA")
    print(f"   - Prix total: {cart_item.total_price} FCFA")
    
    # 8. Créer une commande de test
    order = Order.objects.create(
        user=user,
        subtotal=cart.total_price,
        shipping_cost=Decimal('1000'),
        total=cart.total_price + Decimal('1000')
    )
    print(f"\n8. Commande créée: {order.order_number}")
    
    # 9. Créer l'article de commande
    order_item = OrderItem.objects.create(
        order=order,
        product=product,
        product_name=product.name,
        size='M',
        quantity=1,
        price=product.current_price,
        total_price=cart_item.total_price
    )
    print(f"9. Article de commande créé: {order_item}")
    
    # 10. Copier les personnalisations
    for cart_custom in cart_item.customizations.all():
        order_custom = OrderItemCustomization.objects.create(
            order_item=order_item,
            customization=cart_custom.customization,
            custom_text=cart_custom.custom_text,
            quantity=cart_custom.quantity,
            price=cart_custom.price
        )
        print(f"10. Personnalisation copiée: {order_custom}")
    
    # 11. Vérifier la commande finale
    print(f"\n11. Résumé de la commande:")
    print(f"    - Numéro: {order.order_number}")
    print(f"    - Sous-total: {order.subtotal} FCFA")
    print(f"    - Frais de livraison: {order.shipping_cost} FCFA")
    print(f"    - Total: {order.total} FCFA")
    print(f"    - Personnalisations: {order_item.customizations.count()}")
    
    # 12. Afficher les détails des personnalisations
    print(f"\n12. Détails des personnalisations:")
    for custom in order_item.customizations.all():
        if custom.custom_text:
            print(f"    - {custom.customization.name}: '{custom.custom_text}' (+{custom.price} FCFA)")
        else:
            print(f"    - {custom.customization.name} (+{custom.price} FCFA)")
    
    print(f"\n✅ Test terminé avec succès!")
    print(f"📋 URL de la commande dans l'admin: http://localhost:8000/admin/orders/order/{order.id}/change/")
    print(f"🎨 URL du dashboard personnalisations: http://localhost:8000/dashboard/customizations/")

if __name__ == '__main__':
    test_customizations()

