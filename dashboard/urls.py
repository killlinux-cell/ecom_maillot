from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_home, name='home'),
    
    # Gestion des produits
    path('products/', views.dashboard_products, name='products'),
    path('products/<int:product_id>/edit/', views.dashboard_product_edit, name='product_edit'),
    
    # Gestion des catégories
    path('categories/', views.dashboard_categories, name='categories'),
    
    # Gestion des équipes
    path('teams/', views.dashboard_teams, name='teams'),
    
    # Gestion des utilisateurs
    path('users/', views.dashboard_users, name='users'),
    path('users/<int:user_id>/edit/', views.dashboard_user_edit, name='user_edit'),
    
    # Gestion des commandes
    path('orders/', views.dashboard_orders, name='orders'),
    
    # Gestion des paiements
    path('payments/', views.dashboard_payments, name='payments'),
    
    # Gestion des personnalisations
    path('customizations/', views.dashboard_customizations, name='customizations'),
    
    # Analyses et rapports
    path('analytics/', views.dashboard_analytics, name='analytics'),
    
    # Paramètres
    path('settings/', views.dashboard_settings, name='settings'),
]
