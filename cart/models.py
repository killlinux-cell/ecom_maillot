from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name="Clé de session")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"

    def __str__(self):
        if self.user:
            return f"Panier de {self.user.username}"
        return f"Panier session {self.session_key}"

    @property
    def total_items(self):
        """Retourne le nombre total d'articles dans le panier"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Calcule le prix total du panier"""
        return sum(item.total_price for item in self.items.all())

    def clear(self):
        """Vide le panier"""
        self.items.all().delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Panier")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    size = models.CharField(max_length=10, verbose_name="Taille")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Ajouté le")

    class Meta:
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"
        unique_together = ['cart', 'product', 'size']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} ({self.size})"

    @property
    def total_price(self):
        """Calcule le prix total pour cet article (produit + personnalisations)"""
        base_price = self.product.current_price * self.quantity
        customization_price = sum(cust.price for cust in self.customizations.all())
        return base_price + customization_price
    
    def get_total_price_with_customizations(self):
        """Calcule le prix total avec personnalisations (pour compatibilité)"""
        return self.total_price
    
    @property
    def customization_price(self):
        """Calcule le prix total des personnalisations"""
        return sum(cust.price for cust in self.customizations.all())
    
    @property
    def base_price(self):
        """Calcule le prix de base du produit"""
        return self.product.current_price * self.quantity

    def save(self, *args, **kwargs):
        # Vérifier que la taille est disponible
        if not self.product.is_available_in_size(self.size):
            raise ValueError(f"La taille {self.size} n'est pas disponible pour ce produit")
        
        # Vérifier le stock
        if self.quantity > self.product.get_stock_for_size(self.size):
            raise ValueError(f"Stock insuffisant pour la taille {self.size}")
        
        super().save(*args, **kwargs)
