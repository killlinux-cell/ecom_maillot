from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name="Utilisateur")
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")
    address = models.CharField(max_length=250, verbose_name="Adresse")
    city = models.CharField(max_length=100, verbose_name="Ville")
    postal_code = models.CharField(max_length=20, verbose_name="Code postal")
    country = models.CharField(max_length=100, default="Côte d'Ivoire", verbose_name="Pays")
    is_default = models.BooleanField(default=False, verbose_name="Adresse par défaut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresses"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Désactiver les autres adresses par défaut pour cet utilisateur
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours de traitement'),
        ('shipped', 'Expédié'),
        ('delivered', 'Livré'),
        ('cancelled', 'Annulé'),
        ('refunded', 'Remboursé'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Utilisateur")
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de commande")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="Statut du paiement")
    
    # Adresse de livraison
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, verbose_name="Adresse de livraison")
    
    # Informations de paiement
    payment_method = models.CharField(max_length=50, default='wave', verbose_name="Méthode de paiement")
    payment_id = models.CharField(max_length=100, blank=True, verbose_name="ID de paiement")
    
    # Totaux
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Sous-total")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Frais de livraison")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")
    
    # Notes
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Payé le")

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande {self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Générer un numéro de commande unique
            import datetime
            now = datetime.datetime.now()
            self.order_number = f"CMD{now.strftime('%Y%m%d%H%M%S')}{self.user.id}"
        super().save(*args, **kwargs)

    @property
    def is_paid(self):
        return self.payment_status == 'paid'

    @property
    def can_be_cancelled(self):
        return self.status in ['pending', 'processing']

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Commande")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    product_name = models.CharField(max_length=200, verbose_name="Nom du produit")
    size = models.CharField(max_length=10, verbose_name="Taille")
    quantity = models.PositiveIntegerField(verbose_name="Quantité")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix total")

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"

    def __str__(self):
        return f"{self.quantity}x {self.product_name} ({self.size})"

    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = self.product.name
        if not self.total_price:
            self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)


class OrderItemCustomization(models.Model):
    """Personnalisation appliquée à un article de commande"""
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='customizations', verbose_name="Article de commande")
    customization = models.ForeignKey('products.JerseyCustomization', on_delete=models.CASCADE, verbose_name="Personnalisation")
    custom_text = models.CharField(max_length=50, blank=True, verbose_name="Texte personnalisé")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix total")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Personnalisation d'article de commande"
        verbose_name_plural = "Personnalisations d'articles de commande"
    
    def __str__(self):
        if self.customization.customization_type == 'name' and self.custom_text:
            return f"{self.custom_text} sur {self.order_item.product_name}"
        else:
            return f"{self.customization.name} sur {self.order_item.product_name}"
    
    def save(self, *args, **kwargs):
        # Calculer le prix total
        if self.customization.customization_type == 'name' and self.custom_text:
            # Pour les noms/numéros, le prix dépend du nombre de caractères
            self.price = self.customization.price * len(self.custom_text) * self.quantity
        else:
            # Pour les badges, prix fixe
            self.price = self.customization.price * self.quantity
        super().save(*args, **kwargs)
