from decimal import Decimal
from django.conf import settings
from products.models import Product


class Cart:
    def __init__(self, request):
        """Initialise le panier"""
        self.session = request.session
        self._request = request
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Sauvegarder un panier vide dans la session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, size, quantity=1, override_quantity=False):
        """Ajouter un produit au panier ou mettre à jour sa quantité"""
        product_id = str(product.id)
        size_key = f"{product_id}_{size}"
        
        if size_key not in self.cart:
            self.cart[size_key] = {
                'quantity': 0,
                'price': str(product.current_price),
                'size': size
            }
        
        if override_quantity:
            self.cart[size_key]['quantity'] = quantity
        else:
            self.cart[size_key]['quantity'] += quantity
        
        self.save()
        
        # Retourner le cart_item pour les personnalisations
        from .models import Cart, CartItem
        from django.contrib.auth.models import AnonymousUser
        
        # Créer ou récupérer le panier
        if hasattr(self, '_request') and not isinstance(self._request.user, AnonymousUser):
            cart, created = Cart.objects.get_or_create(user=self._request.user)
        else:
            cart, created = Cart.objects.get_or_create(session_key=self._request.session.session_key)
        
        # Créer ou récupérer le cart_item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )
        
        if not created:
            if override_quantity:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item

    def save(self):
        """Marquer la session comme "modifiée" pour s'assurer qu'elle est sauvegardée"""
        self.session.modified = True

    def remove(self, product, size):
        """Supprimer un produit du panier"""
        product_id = str(product.id)
        size_key = f"{product_id}_{size}"
        
        if size_key in self.cart:
            del self.cart[size_key]
            self.save()

    def __iter__(self):
        """Itérer sur les articles du panier et obtenir les produits de la base de données"""
        product_ids = []
        for key in self.cart.keys():
            product_id = key.split('_')[0]
            if product_id not in product_ids:
                product_ids.append(product_id)
        
        # Obtenir les objets produit et les ajouter au panier
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            product_id = str(product.id)
            for key in cart.keys():
                if key.startswith(product_id + '_'):
                    cart[key]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Compter tous les articles dans le panier"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculer le coût total des articles dans le panier avec personnalisations"""
        total = 0
        
        # Récupérer les cart_items avec leurs personnalisations
        from .models import Cart, CartItem
        from django.contrib.auth.models import AnonymousUser
        
        if hasattr(self, '_request') and not isinstance(self._request.user, AnonymousUser):
            cart = Cart.objects.filter(user=self._request.user).first()
        else:
            cart = Cart.objects.filter(session_key=self._request.session.session_key).first()
        
        if cart:
            # Utiliser les cart_items qui ont déjà les personnalisations calculées
            for cart_item in cart.items.all():
                total += cart_item.total_price
        else:
            # Fallback : calcul basique sans personnalisations
            for item in self.cart.values():
                base_price = Decimal(item['price']) * item['quantity']
                total += base_price
        
        return total

    def clear(self):
        """Supprimer le panier de la session"""
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_item(self, product, size):
        """Obtenir un article spécifique du panier"""
        product_id = str(product.id)
        size_key = f"{product_id}_{size}"
        return self.cart.get(size_key)

    def update_quantity(self, product, size, quantity):
        """Mettre à jour la quantité d'un article"""
        if quantity > 0:
            self.add(product, size, quantity, override_quantity=True)
        else:
            self.remove(product, size)
