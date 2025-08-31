from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .models import Order, OrderItem, Address, OrderItemCustomization
from .forms import OrderCreateForm, AddressForm
from cart.cart import Cart


@login_required
def order_create(request):
    """Créer une nouvelle commande"""
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, "Votre panier est vide.")
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Créer la commande
                order = form.save(commit=False)
                order.user = request.user
                
                # Calculer les totaux
                subtotal = cart.get_total_price()
                shipping_cost = Decimal('1000')  # Frais de livraison fixes
                total = subtotal + shipping_cost
                
                order.subtotal = subtotal
                order.shipping_cost = shipping_cost
                order.total = total
                order.save()
                
                # Créer les articles de commande avec personnalisations
                for item in cart:
                    # Récupérer le cart_item pour les personnalisations
                    from cart.models import CartItem
                    cart_item = CartItem.objects.filter(
                        cart__user=request.user,
                        product=item['product'],
                        size=item['size']
                    ).first()
                    
                    # Calculer le prix total avec personnalisations
                    if cart_item:
                        total_price = cart_item.total_price
                    else:
                        total_price = item['total_price']
                    
                    # Créer l'article de commande
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        product_name=item['product'].name,
                        size=item['size'],
                        quantity=item['quantity'],
                        price=item['price'],
                        total_price=total_price
                    )
                    
                    # Copier les personnalisations du cart_item vers l'order_item
                    if cart_item:
                        for cart_custom in cart_item.customizations.all():
                            OrderItemCustomization.objects.create(
                                order_item=order_item,
                                customization=cart_custom.customization,
                                custom_text=cart_custom.custom_text,
                                quantity=cart_custom.quantity,
                                price=cart_custom.price
                            )
                
                # Vider le panier
                cart.clear()
                
                messages.success(request, f"Commande {order.order_number} créée avec succès.")
                
                # Rediriger selon la méthode de paiement choisie
                payment_method = request.POST.get('payment_method', 'paydunya')
                if payment_method == 'wave_direct':
                    return redirect('payments:wave_direct_payment', order_id=order.id)
                
                else:
                    return redirect('payments:process_payment', order_id=order.id)
    else:
        form = OrderCreateForm()
    
    context = {
        'cart': cart,
        'form': form,
    }
    return render(request, 'orders/order_create.html', context)


@login_required
def order_detail(request, order_id):
    """Afficher le détail d'une commande"""
    # Permettre aux administrateurs de voir toutes les commandes
    if request.user.is_staff or request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
    else:
        # Les utilisateurs normaux ne peuvent voir que leurs propres commandes
        order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_list(request):
    """Liste des commandes de l'utilisateur"""
    # Permettre aux administrateurs de voir toutes les commandes
    if request.user.is_staff or request.user.is_superuser:
        orders = Order.objects.all().order_by('-created_at')
    else:
        # Les utilisateurs normaux ne peuvent voir que leurs propres commandes
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_cancel(request, order_id):
    """Annuler une commande"""
    # Permettre aux administrateurs d'annuler n'importe quelle commande
    if request.user.is_staff or request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
    else:
        # Les utilisateurs normaux ne peuvent annuler que leurs propres commandes
        order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.can_be_cancelled:
        order.status = 'cancelled'
        order.save()
        messages.success(request, f"Commande {order.order_number} annulée avec succès.")
    else:
        messages.error(request, "Cette commande ne peut pas être annulée.")
    
    return redirect('orders:order_detail', order_id=order.id)


@login_required
def address_create(request):
    """Créer une nouvelle adresse"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Adresse ajoutée avec succès.")
            return redirect('orders:order_create')
    else:
        form = AddressForm()
    
    context = {
        'form': form,
    }
    return render(request, 'orders/address_form.html', context)
