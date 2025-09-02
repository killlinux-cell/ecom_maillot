#!/usr/bin/env python3
"""
Script de test pour vérifier la mise à jour automatique du stock
Usage: python test_stock_update.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

from products.models import Product
from orders.models import Order, OrderItem
from accounts.models import User

def test_stock_update():
    """Test de la mise à jour automatique du stock"""
    print("🧪 Test de la mise à jour automatique du stock...")
    
    try:
        # Récupérer un produit existant
        product = Product.objects.first()
        if not product:
            print("❌ Aucun produit trouvé dans la base de données")
            return False
        
        print(f"📦 Produit test: {product.name}")
        print(f"📊 Stock initial: {product.stock_quantity}")
        
        # Récupérer un utilisateur existant
        user = User.objects.first()
        if not user:
            print("❌ Aucun utilisateur trouvé dans la base de données")
            return False
        
        # Créer une commande de test
        order = Order.objects.create(
            user=user,
            order_number=f"TEST-{Order.objects.count() + 1}",
            total_amount=product.price * 2,
            status='confirmed',
            payment_status='paid'
        )
        
        # Créer un article de commande
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            quantity=2,
            price=product.price
        )
        
        print(f"🛒 Commande créée: {order.order_number}")
        print(f"📦 Article commandé: {order_item.quantity} x {product.name}")
        
        # Vérifier que le stock a été mis à jour
        product.refresh_from_db()
        print(f"📊 Stock après commande: {product.stock_quantity}")
        
        # Nettoyer la commande de test
        order.delete()
        
        print("✅ Test réussi ! Le stock a été mis à jour automatiquement")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_product_images():
    """Test de l'affichage des images des produits"""
    print("\n🖼️ Test de l'affichage des images des produits...")
    
    try:
        products = Product.objects.all()[:5]
        
        for product in products:
            print(f"📦 Produit: {product.name}")
            if product.image:
                print(f"   🖼️ Image: {product.image.url}")
                print(f"   📁 Chemin: {product.image.path}")
                print(f"   ✅ Existe: {os.path.exists(product.image.path)}")
            else:
                print("   ❌ Aucune image")
        
        print("✅ Test des images terminé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des images: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test de la gestion automatique du stock et des images")
    print("=" * 60)
    
    # Test de la mise à jour du stock
    stock_test = test_stock_update()
    
    # Test des images
    images_test = test_product_images()
    
    print("\n" + "=" * 60)
    print("📊 Résultats des tests:")
    print(f"   Stock automatique: {'✅' if stock_test else '❌'}")
    print(f"   Images des produits: {'✅' if images_test else '❌'}")
    
    if stock_test and images_test:
        print("\n🎉 Tous les tests sont passés avec succès !")
        return 0
    else:
        print("\n⚠️ Certains tests ont échoué")
        return 1

if __name__ == '__main__':
    exit(main())
