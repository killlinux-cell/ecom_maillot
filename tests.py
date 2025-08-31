"""
Tests pour l'application e-commerce de maillots de football
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from products.models import Category, Team, Product
from orders.models import Order, Address
from cart.cart import Cart


class ProductModelTest(TestCase):
    """Tests pour les modèles de produits"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.category = Category.objects.create(
            name="Maillots Domicile",
            description="Maillots officiels de domicile"
        )
        
        self.team = Team.objects.create(
            name="Real Madrid",
            country="Espagne",
            league="La Liga"
        )
        
        self.product = Product.objects.create(
            name="Maillot Real Madrid Domicile",
            category=self.category,
            team=self.team,
            description="Maillot officiel de domicile",
            price=Decimal('15000'),
            available_sizes=['S', 'M', 'L', 'XL'],
            stock_quantity=20
        )
    
    def test_product_creation(self):
        """Test de création d'un produit"""
        self.assertEqual(self.product.name, "Maillot Real Madrid Domicile")
        self.assertEqual(self.product.price, Decimal('15000'))
        self.assertEqual(self.product.stock_quantity, 20)
    
    def test_product_current_price(self):
        """Test du prix actuel d'un produit"""
        self.assertEqual(self.product.current_price, Decimal('15000'))
        
        # Test avec prix en promotion
        self.product.sale_price = Decimal('12000')
        self.product.save()
        self.assertEqual(self.product.current_price, Decimal('12000'))
    
    def test_product_discount_percentage(self):
        """Test du calcul du pourcentage de réduction"""
        self.product.sale_price = Decimal('12000')
        self.product.save()
        self.assertEqual(self.product.discount_percentage, 20)
    
    def test_product_is_on_sale(self):
        """Test si un produit est en promotion"""
        self.assertFalse(self.product.is_on_sale)
        
        self.product.sale_price = Decimal('12000')
        self.product.save()
        self.assertTrue(self.product.is_on_sale)


class CartTest(TestCase):
    """Tests pour le panier"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        self.category = Category.objects.create(name="Test Category")
        self.team = Team.objects.create(name="Test Team", country="Test")
        
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            team=self.team,
            description="Test description",
            price=Decimal('10000'),
            available_sizes=['M', 'L'],
            stock_quantity=10
        )
    
    def test_cart_add_product(self):
        """Test d'ajout d'un produit au panier"""
        response = self.client.post(reverse('cart:cart_add'), {
            'product_id': self.product.id,
            'size': 'M',
            'quantity': 2
        })
        
        self.assertEqual(response.status_code, 302)  # Redirection
        
        # Vérifier que le produit est dans le panier
        cart = Cart(self.client)
        self.assertEqual(len(cart), 2)
    
    def test_cart_remove_product(self):
        """Test de suppression d'un produit du panier"""
        # Ajouter un produit
        self.client.post(reverse('cart:cart_add'), {
            'product_id': self.product.id,
            'size': 'M',
            'quantity': 1
        })
        
        # Supprimer le produit
        response = self.client.post(reverse('cart:cart_remove'), {
            'product_id': self.product.id,
            'size': 'M'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que le panier est vide
        cart = Cart(self.client)
        self.assertEqual(len(cart), 0)


class OrderTest(TestCase):
    """Tests pour les commandes"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.address = Address.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            phone='+2250123456789',
            email='test@example.com',
            address='123 Test Street',
            city='Abidjan',
            postal_code='12345',
            country="Côte d'Ivoire"
        )
        
        self.category = Category.objects.create(name="Test Category")
        self.team = Team.objects.create(name="Test Team", country="Test")
        
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            team=self.team,
            description="Test description",
            price=Decimal('10000'),
            available_sizes=['M'],
            stock_quantity=10
        )
    
    def test_order_creation(self):
        """Test de création d'une commande"""
        order = Order.objects.create(
            user=self.user,
            shipping_address=self.address,
            subtotal=Decimal('10000'),
            shipping_cost=Decimal('1000'),
            total=Decimal('11000')
        )
        
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total, Decimal('11000'))
        self.assertEqual(order.payment_status, 'pending')
    
    def test_order_number_generation(self):
        """Test de génération automatique du numéro de commande"""
        order = Order.objects.create(
            user=self.user,
            shipping_address=self.address,
            subtotal=Decimal('10000'),
            shipping_cost=Decimal('1000'),
            total=Decimal('11000')
        )
        
        self.assertTrue(order.order_number.startswith('CMD'))
        self.assertIsNotNone(order.order_number)


class ViewTest(TestCase):
    """Tests pour les vues"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name="Test Category")
        self.team = Team.objects.create(name="Test Team", country="Test")
        
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            team=self.team,
            description="Test description",
            price=Decimal('10000'),
            available_sizes=['M'],
            stock_quantity=10,
            is_active=True
        )
    
    def test_home_page(self):
        """Test de la page d'accueil"""
        response = self.client.get(reverse('products:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/home.html')
    
    def test_product_list_page(self):
        """Test de la page de liste des produits"""
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')
    
    def test_product_detail_page(self):
        """Test de la page de détail d'un produit"""
        response = self.client.get(reverse('products:product_detail', args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
    
    def test_cart_page(self):
        """Test de la page du panier"""
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart_detail.html')
    
    def test_search_functionality(self):
        """Test de la fonctionnalité de recherche"""
        response = self.client.get(reverse('products:search'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/search.html')


class AuthenticationTest(TestCase):
    """Tests pour l'authentification"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login(self):
        """Test de connexion"""
        response = self.client.post(reverse('account_login'), {
            'login': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirection après connexion
    
    def test_logout(self):
        """Test de déconnexion"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('account_logout'))
        self.assertEqual(response.status_code, 302)  # Redirection après déconnexion


if __name__ == '__main__':
    # Exécuter les tests
    import django
    django.setup()
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'test'])
