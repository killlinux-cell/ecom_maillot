from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('orders/', views.dashboard_orders, name='orders'),
    path('products/', views.dashboard_products, name='products'),
    path('users/', views.dashboard_users, name='users'),
    path('analytics/', views.dashboard_analytics, name='analytics'),
    path('payments/', views.dashboard_payments, name='payments'),
    path('customizations/', views.dashboard_customizations, name='customizations'),
]
