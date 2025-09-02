from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from products.models import Product, Category, Team, JerseyCustomization
from orders.models import Order, OrderItem
from payments.models import Payment
from django.contrib.auth.models import User
from cart.models import Cart, CartItem
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
    total_users = User.objects.filter(is_staff=False).count()  # Seulement les clients (non-staff)
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
    
    # Statistiques des utilisateurs
    new_users_7_days = User.objects.filter(
        date_joined__date__gte=last_7_days,
        is_staff=False
    ).count()
    
    new_users_30_days = User.objects.filter(
        date_joined__date__gte=last_30_days,
        is_staff=False
    ).count()
    
    # Utilisateurs avec commandes
    users_with_orders = User.objects.filter(
        orders__isnull=False,
        is_staff=False
    ).distinct().count()
    
    # Calcul du taux d'engagement
    engagement_rate = 0
    if total_users > 0:
        engagement_rate = round((users_with_orders / total_users) * 100, 1)
    
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
        'new_users_7_days': new_users_7_days,
        'new_users_30_days': new_users_30_days,
        'users_with_orders': users_with_orders,
        'engagement_rate': engagement_rate,
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
    
    # Base des commandes pour les filtres
    orders = Order.objects.select_related('user', 'shipping_address').order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Statistiques GLOBALES (toutes les commandes, pas seulement les filtrées)
    all_orders = Order.objects.all()
    
    # Total des commandes
    total_orders_count = all_orders.count()
    
    # Commandes en attente
    pending_orders_count = all_orders.filter(status='pending').count()
    
    # Commandes livrées
    delivered_orders_count = all_orders.filter(status='delivered').count()
    
    # Revenus totaux (commandes payées)
    total_revenue = all_orders.filter(payment_status='paid').aggregate(
        total=Sum('total')
    )['total'] or 0
    
    # Pagination des commandes filtrées
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'total_orders_count': total_orders_count,
        'pending_orders_count': pending_orders_count,
        'delivered_orders_count': delivered_orders_count,
        'total_revenue': total_revenue,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'dashboard/orders.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_products(request):
    """Gestion des produits"""
    products = Product.objects.select_related('category', 'team').order_by('-created_at')
    
    # Filtres
    category_filter = request.GET.get('category', '')
    team_filter = request.GET.get('team', '')
    search_query = request.GET.get('search', '')
    
    if category_filter:
        products = products.filter(category__slug=category_filter)
    if team_filter:
        products = products.filter(team__slug=team_filter)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    teams = Team.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'teams': teams,
        'current_category': category_filter,
        'current_team': team_filter,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/products.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_product_edit(request, product_id):
    """Édition d'un produit"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Logique de mise à jour du produit
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.sale_price = request.POST.get('sale_price') or None
        product.stock_quantity = request.POST.get('stock_quantity')
        product.is_active = request.POST.get('is_active') == 'on'
        product.is_featured = request.POST.get('is_featured') == 'on'
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        messages.success(request, 'Produit mis à jour avec succès!')
        return redirect('dashboard:products')
    
    categories = Category.objects.all()
    teams = Team.objects.all()
    
    context = {
        'product': product,
        'categories': categories,
        'teams': teams,
    }
    
    return render(request, 'dashboard/product_edit.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_categories(request):
    """Gestion des catégories"""
    categories = Category.objects.all().order_by('name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            Category.objects.create(name=name, description=description)
            messages.success(request, 'Catégorie créée avec succès!')
            return redirect('dashboard:categories')
    
    context = {'categories': categories}
    return render(request, 'dashboard/categories.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_teams(request):
    """Gestion des équipes"""
    teams = Team.objects.all().order_by('name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        country = request.POST.get('country')
        league = request.POST.get('league')
        
        if name and country:
            Team.objects.create(name=name, country=country, league=league)
            messages.success(request, 'Équipe créée avec succès!')
            return redirect('dashboard:teams')
    
    context = {'teams': teams}
    return render(request, 'dashboard/teams.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_users(request):
    """Gestion des utilisateurs"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filtres
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/users.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_user_edit(request, user_id):
    """Édition d'un utilisateur"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        
        # Gestion du mot de passe
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        messages.success(request, 'Utilisateur mis à jour avec succès!')
        return redirect('dashboard:users')
    
    context = {'user': user}
    return render(request, 'dashboard/user_edit.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_customizations(request):
    """Gestion des personnalisations"""
    customizations = JerseyCustomization.objects.all().order_by('-created_at')
    
    # Filtres
    product_filter = request.GET.get('product', '')
    if product_filter:
        # Filtrer par type de personnalisation au lieu de produit
        customizations = customizations.filter(customization_type=product_filter)
    
    # Pagination
    paginator = Paginator(customizations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Récupérer tous les types de personnalisation disponibles
    customization_types = JerseyCustomization.CUSTOMIZATION_TYPES
    
    context = {
        'customizations': page_obj,
        'customization_types': customization_types,
        'current_type': product_filter,
    }
    
    return render(request, 'dashboard/customizations.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_analytics(request):
    """Analyses et rapports"""
    
    # Statistiques des ventes par mois
    current_year = timezone.now().year
    monthly_sales = []
    
    for month in range(1, 13):
        month_start = timezone.datetime(current_year, month, 1, tzinfo=timezone.utc)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_revenue = Order.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end,
            payment_status='paid'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        month_orders = Order.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()
        
        monthly_sales.append({
            'month': month_start.strftime('%B'),
            'revenue': month_revenue,
            'orders': month_orders
        })
    
    # Top 10 des produits les plus vendus
    top_products = OrderItem.objects.values('product_name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_sold')[:10]
    
    # Statistiques des équipes
    team_stats = Team.objects.annotate(
        product_count=Count('products'),
        total_sales=Sum('products__orderitem__quantity', default=0)
    ).order_by('-total_sales')
    
    context = {
        'monthly_sales': monthly_sales,
        'top_products': top_products,
        'team_stats': team_stats,
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
def dashboard_settings(request):
    """Paramètres du système"""
    if request.method == 'POST':
        # Ici vous pouvez ajouter la logique pour sauvegarder les paramètres
        messages.success(request, 'Paramètres mis à jour avec succès!')
        return redirect('dashboard:settings')
    
    context = {}
    return render(request, 'dashboard/settings.html', context)
