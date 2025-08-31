from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='categories/', blank=True, verbose_name="Image")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:category_detail', args=[self.slug])


class Team(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom de l'équipe")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    country = models.CharField(max_length=100, verbose_name="Pays")
    league = models.CharField(max_length=100, blank=True, verbose_name="Ligue")
    logo = models.ImageField(upload_to='teams/', blank=True, verbose_name="Logo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Équipe"
        verbose_name_plural = "Équipes"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    SIZES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', '2XL'),
        ('XXXL', '3XL'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nom")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Catégorie")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='products', verbose_name="Équipe")
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Prix en promotion")
    available_sizes = models.JSONField(default=list, verbose_name="Tailles disponibles")
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Quantité en stock")
    is_featured = models.BooleanField(default=False, verbose_name="Produit vedette")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.slug])

    @property
    def current_price(self):
        """Retourne le prix actuel (promotion ou prix normal)"""
        return self.sale_price if self.sale_price else self.price

    @property
    def discount_percentage(self):
        """Calcule le pourcentage de réduction"""
        if self.sale_price and self.price > self.sale_price:
            return int(((self.price - self.sale_price) / self.price) * 100)
        return 0

    @property
    def is_on_sale(self):
        """Vérifie si le produit est en promotion"""
        return bool(self.sale_price and self.sale_price < self.price)

    @property
    def is_available(self):
        """Vérifie si le produit est disponible (en stock et actif)"""
        return self.stock_quantity > 0 and self.is_active

    def is_available_in_size(self, size):
        """Vérifie si une taille est disponible"""
        return size in self.available_sizes

    def get_stock_for_size(self, size):
        """Retourne le stock pour une taille donnée"""
        # Pour simplifier, on considère que le stock est global
        # Dans une version plus avancée, on pourrait avoir un modèle Stock par taille
        return self.stock_quantity


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Produit")
    image = models.ImageField(upload_to='products/', verbose_name="Image")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Texte alternatif")
    is_primary = models.BooleanField(default=False, verbose_name="Image principale")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Image de produit"
        verbose_name_plural = "Images de produits"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image de {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Désactiver les autres images principales pour ce produit
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Produit")
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="Utilisateur")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note"
    )
    comment = models.TextField(verbose_name="Commentaire")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"Avis de {self.user.username} sur {self.product.name}"


class JerseyCustomization(models.Model):
    """Options de personnalisation pour les maillots"""
    CUSTOMIZATION_TYPES = [
        ('name', 'Nom/Numéro'),
        ('badge', 'Badge/Emblème'),
        ('sponsor', 'Sponsor'),
    ]
    
    BADGE_TYPES = [
        ('liga', 'Liga'),
        ('uefa', 'UEFA'),
        ('champions', 'Champions League'),
        ('europa', 'Europa League'),
        ('premier', 'Premier League'),
        ('bundesliga', 'Bundesliga'),
        ('serie_a', 'Serie A'),
        ('ligue_1', 'Ligue 1'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom de l'option")
    customization_type = models.CharField(max_length=20, choices=CUSTOMIZATION_TYPES, verbose_name="Type de personnalisation")
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES, blank=True, verbose_name="Type de badge")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Personnalisation de maillot"
        verbose_name_plural = "Personnalisations de maillots"
        ordering = ['customization_type', 'name']
        unique_together = ['customization_type', 'badge_type', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.get_customization_type_display()} ({self.price} FCFA)"
    
    @property
    def display_name(self):
        if self.customization_type == 'name':
            return f"Nom/Numéro ({self.price} FCFA par caractère)"
        elif self.customization_type == 'badge':
            return f"Badge {self.get_badge_type_display()} ({self.price} FCFA)"
        else:
            return f"{self.name} ({self.price} FCFA)"
    
    @classmethod
    def get_or_create_name_customization(cls):
        """Récupérer ou créer l'option de personnalisation nom/numéro"""
        try:
            return cls.objects.get(
                customization_type='name',
                name='Nom et Numéro'
            )
        except cls.DoesNotExist:
            return cls.objects.create(
                customization_type='name',
                name='Nom et Numéro',
                price=500.00,
                description='Ajoutez votre nom et numéro sur le maillot. Prix: 500 FCFA par caractère.'
            )
    
    @classmethod
    def get_or_create_badge_customization(cls, badge_type):
        """Récupérer ou créer l'option de personnalisation badge"""
        badge_name = f"Badge {badge_type.title()}"
        try:
            return cls.objects.get(
                customization_type='badge',
                badge_type=badge_type,
                name=badge_name
            )
        except cls.DoesNotExist:
            return cls.objects.create(
                customization_type='badge',
                badge_type=badge_type,
                name=badge_name,
                price=500.00,
                description=f'Badge officiel {badge_type}'
            )


class CartItemCustomization(models.Model):
    """Personnalisation appliquée à un article du panier"""
    cart_item = models.ForeignKey('cart.CartItem', on_delete=models.CASCADE, related_name='customizations', verbose_name="Article du panier")
    customization = models.ForeignKey(JerseyCustomization, on_delete=models.CASCADE, verbose_name="Personnalisation")
    custom_text = models.CharField(max_length=50, blank=True, verbose_name="Texte personnalisé")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix total")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Personnalisation d'article"
        verbose_name_plural = "Personnalisations d'articles"
    
    def __str__(self):
        if self.customization.customization_type == 'name' and self.custom_text:
            return f"{self.custom_text} sur {self.cart_item.product.name}"
        else:
            return f"{self.customization.name} sur {self.cart_item.product.name}"
    
    def save(self, *args, **kwargs):
        # Calculer le prix total
        if self.customization.customization_type == 'name' and self.custom_text:
            # Pour les noms/numéros, le prix dépend du nombre de caractères
            self.price = self.customization.price * len(self.custom_text) * self.quantity
        else:
            # Pour les badges, prix fixe
            self.price = self.customization.price * self.quantity
        super().save(*args, **kwargs)
