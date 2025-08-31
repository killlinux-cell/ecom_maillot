from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from products.models import Product, Category, Team
from orders.models import Order, OrderItem
from payments.models import Payment
from django.contrib.auth.models import User
import json

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def dashboard_home(request):
    """Dashboard principal avec toutes les statistiques"""
    
    # Périodes pour les statistiques
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    # Statistiques générales
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    total_revenue = Order.objects.filter(payment_status='paid').aggregate(
        total=Sum('total')
    )['total'] or 0
    
    # Commandes récentes
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Produits les plus vendus
    top_products = OrderItem.objects.values('product_name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    
    # Statistiques des 7 derniers jours
    orders_7_days = Order.objects.filter(created_at__date__gte=last_7_days).count()
    revenue_7_days = Order.objects.filter(
        created_at__date__gte=last_7_days,
        payment_status='paid'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Commandes par statut
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Produits en rupture de stock
    out_of_stock_products = Product.objects.filter(
        stock_quantity__lte=0
    ).count()
    
    # Produits en promotion
    products_on_sale = Product.objects.filter(sale_price__isnull=False, sale_price__lt=F('price')).count()
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'orders_7_days': orders_7_days,
        'revenue_7_days': revenue_7_days,
        'orders_by_status': list(orders_by_status),
        'out_of_stock_products': out_of_stock_products,
        'products_on_sale': products_on_sale,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_orders(request):
    """Dashboard des commandes"""
    
    # Filtres
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    orders = Order.objects.select_related('user', 'shipping_address').order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Statistiques des commandes
    total_orders = orders.count()
    total_revenue = orders.filter(payment_status='paid').aggregate(
        total=Sum('total')
    )['total'] or 0
    
    # Commandes par statut
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'orders_by_status': list(orders_by_status),
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'dashboard/orders.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_products(request):
    """Dashboard des produits"""
    
    # Filtres
    category_filter = request.GET.get('category', '')
    team_filter = request.GET.get('team', '')
    availability_filter = request.GET.get('availability', '')
    
    products = Product.objects.select_related('category', 'team').order_by('-created_at')
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    if team_filter:
        products = products.filter(team_id=team_filter)
    
    if availability_filter == 'in_stock':
        products = products.filter(stock_quantity__gt=0)
    elif availability_filter == 'out_of_stock':
        products = products.filter(stock_quantity__lte=0)
    elif availability_filter == 'on_sale':
        products = products.filter(sale_price__isnull=False, sale_price__lt=F('price'))
    
    # Statistiques des produits
    total_products = products.count()
    total_categories = Category.objects.count()
    total_teams = Team.objects.count()
    
    # Produits par catégorie
    products_by_category = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count')
    
    # Produits par équipe
    products_by_team = Team.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count')
    
    # Produits en rupture de stock
    out_of_stock = products.filter(stock_quantity__lte=0).count()
    
    # Produits en promotion
    on_sale = products.filter(sale_price__isnull=False, sale_price__lt=F('price')).count()
    
    context = {
        'products': products,
        'total_products': total_products,
        'total_categories': total_categories,
        'total_teams': total_teams,
        'products_by_category': products_by_category,
        'products_by_team': products_by_team,
        'out_of_stock': out_of_stock,
        'on_sale': on_sale,
        'categories': Category.objects.all(),
        'teams': Team.objects.all(),
        'category_filter': category_filter,
        'team_filter': team_filter,
        'availability_filter': availability_filter,
    }
    
    return render(request, 'dashboard/products.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_users(request):
    """Dashboard des utilisateurs"""
    
    # Filtres
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    users = User.objects.order_by('-date_joined')
    
    if date_from:
        users = users.filter(date_joined__date__gte=date_from)
    
    if date_to:
        users = users.filter(date_joined__date__lte=date_to)
    
    # Statistiques des utilisateurs
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    staff_users = users.filter(is_staff=True).count()
    
    # Utilisateurs avec le plus de commandes
    top_customers = User.objects.annotate(
        order_count=Count('orders')
    ).filter(order_count__gt=0).order_by('-order_count')[:10]
    
    context = {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'top_customers': top_customers,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'dashboard/users.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_analytics(request):
    """Dashboard des analyses et graphiques"""
    
    # Données pour les graphiques
    today = timezone.now().date()
    
    # Commandes des 30 derniers jours
    daily_orders = []
    daily_revenue = []
    
    for i in range(30):
        date = today - timedelta(days=i)
        orders_count = Order.objects.filter(created_at__date=date).count()
        revenue = Order.objects.filter(
            created_at__date=date,
            payment_status='paid'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        daily_orders.append({
            'date': date.strftime('%d/%m'),
            'count': orders_count
        })
        
        daily_revenue.append({
            'date': date.strftime('%d/%m'),
            'amount': float(revenue)
        })
    
    daily_orders.reverse()
    daily_revenue.reverse()
    
    # Produits les plus vendus
    top_products = OrderItem.objects.values('product_name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_sold')[:10]
    
    # Catégories les plus populaires
    top_categories = OrderItem.objects.values('product__category__name').annotate(
        total_sold=Sum('quantity')
    ).filter(product__category__isnull=False).order_by('-total_sold')[:5]
    
    # Équipes les plus populaires
    top_teams = OrderItem.objects.values('product__team__name').annotate(
        total_sold=Sum('quantity')
    ).filter(product__team__isnull=False).order_by('-total_sold')[:5]
    
    context = {
        'daily_orders': json.dumps(daily_orders),
        'daily_revenue': json.dumps(daily_revenue),
        'top_products': list(top_products),
        'top_categories': list(top_categories),
        'top_teams': list(top_teams),
    }
    
    return render(request, 'dashboard/analytics.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_payments(request):
    """Dashboard des paiements"""
    
    # Filtres
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    payments = Payment.objects.select_related('order', 'order__user').order_by('-created_at')
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    if date_from:
        payments = payments.filter(created_at__date__gte=date_from)
    
    if date_to:
        payments = payments.filter(created_at__date__lte=date_to)
    
    # Statistiques des paiements
    total_payments = payments.count()
    total_amount = payments.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Paiements par statut
    payments_by_status = Payment.objects.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    ).order_by('status')
    
    context = {
        'payments': payments,
        'total_payments': total_payments,
        'total_amount': total_amount,
        'payments_by_status': list(payments_by_status),
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'dashboard/payments.html', context)


@login_required
@user_passes_test(is_admin)
def dashboard_customizations(request):
    """Dashboard des personnalisations pour la livraison"""
    
    # Filtres
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Récupérer les commandes avec personnalisations
    orders = Order.objects.prefetch_related(
        'items__customizations__customization'
    ).filter(
        items__customizations__isnull=False
    ).distinct().order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Statistiques des personnalisations
    total_orders_with_customizations = orders.count()
    total_customizations = OrderItem.objects.filter(
        customizations__isnull=False
    ).count()
    
    # Personnalisations par type
    customizations_by_type = OrderItem.objects.filter(
        customizations__isnull=False
    ).values(
        'customizations__customization__customization_type'
    ).annotate(
        count=Count('customizations')
    ).order_by('customizations__customization__customization_type')
    
    context = {
        'orders': orders,
        'total_orders_with_customizations': total_orders_with_customizations,
        'total_customizations': total_customizations,
        'customizations_by_type': list(customizations_by_type),
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'dashboard/customizations.html', context)
