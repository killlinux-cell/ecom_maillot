from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Product
from orders.models import Order, OrderItem

@receiver(post_save, sender=Order)
def update_product_stock_on_order(sender, instance, created, **kwargs):
    """
    Met à jour automatiquement le stock des produits lors de la création/modification d'une commande
    """
    if created or instance.status in ['confirmed', 'shipped', 'delivered']:
        # Récupérer tous les articles de la commande
        order_items = OrderItem.objects.filter(order=instance)
        
        with transaction.atomic():
            for item in order_items:
                try:
                    # Récupérer le produit
                    product = Product.objects.get(id=item.product_id)
                    
                    # Mettre à jour le stock
                    if instance.status in ['confirmed', 'shipped', 'delivered']:
                        # Diminuer le stock lors de la confirmation/expédition/livraison
                        new_stock = max(0, product.stock_quantity - item.quantity)
                        product.stock_quantity = new_stock
                        
                        # Marquer le produit comme en rupture si le stock est à 0
                        if new_stock == 0:
                            product.is_active = False
                        
                        product.save()
                        
                        print(f"Stock mis à jour pour {product.name}: {new_stock} restants")
                    
                except Product.DoesNotExist:
                    print(f"Produit {item.product_id} non trouvé")
                except Exception as e:
                    print(f"Erreur lors de la mise à jour du stock: {e}")

@receiver(post_save, sender=Order)
def restore_stock_on_cancellation(sender, instance, **kwargs):
    """
    Restaure le stock si une commande est annulée
    """
    if instance.status == 'cancelled':
        # Récupérer tous les articles de la commande
        order_items = OrderItem.objects.filter(order=instance)
        
        with transaction.atomic():
            for item in order_items:
                try:
                    # Récupérer le produit
                    product = Product.objects.get(id=item.product_id)
                    
                    # Restaurer le stock
                    product.stock_quantity += item.quantity
                    
                    # Réactiver le produit s'il était en rupture
                    if not product.is_active and product.stock_quantity > 0:
                        product.is_active = True
                    
                    product.save()
                    
                    print(f"Stock restauré pour {product.name}: {product.stock_quantity} disponibles")
                    
                except Product.DoesNotExist:
                    print(f"Produit {item.product_id} non trouvé")
                except Exception as e:
                    print(f"Erreur lors de la restauration du stock: {e}")

@receiver(post_save, sender=Order)
def update_product_sales_count(sender, instance, created, **kwargs):
    """
    Met à jour le compteur de ventes des produits
    """
    if instance.status in ['confirmed', 'shipped', 'delivered']:
        order_items = OrderItem.objects.filter(order=instance)
        
        for item in order_items:
            try:
                product = Product.objects.get(id=item.product_id)
                
                # Incrémenter le compteur de ventes
                if not hasattr(product, 'sales_count'):
                    product.sales_count = 0
                product.sales_count += item.quantity
                product.save()
                
            except Product.DoesNotExist:
                pass
            except Exception as e:
                print(f"Erreur lors de la mise à jour du compteur de ventes: {e}")
