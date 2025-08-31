from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product
from .cart import Cart


def cart_detail(request):
    """Afficher le détail du panier avec personnalisations"""
    cart = Cart(request)
    
    # Récupérer les cart_items avec leurs personnalisations
    cart_items = []
    for item in cart:
        # Récupérer le cart_item de la base de données pour les personnalisations
        from .models import CartItem
        from django.contrib.auth.models import AnonymousUser
        
        if not isinstance(request.user, AnonymousUser):
            cart_item = CartItem.objects.filter(
                cart__user=request.user,
                product=item['product'],
                size=item['size']
            ).first()
        else:
            cart_item = CartItem.objects.filter(
                cart__session_key=request.session.session_key,
                product=item['product'],
                size=item['size']
            ).first()
        
        if cart_item:
            item['customizations'] = cart_item.customizations.all()
        else:
            item['customizations'] = []
        
        # Calculer le prix total avec personnalisations
        base_price = item['price'] * item['quantity']
        customization_price = sum(cust.price for cust in item['customizations'])
        item['total_price_with_customizations'] = base_price + customization_price
        
        cart_items.append(item)
    
    # Calculer le total avec personnalisations
    total_with_customizations = 0
    for item in cart_items:
        base_price = item['price'] * item['quantity']
        customization_price = sum(cust.price for cust in item.get('customizations', []))
        total_with_customizations += base_price + customization_price
    
    context = {
        'cart_items': cart_items,
        'cart': cart,
        'total_with_customizations': total_with_customizations
    }
    
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def cart_add(request):
    """Ajouter un produit au panier avec personnalisations"""
    product_id = request.POST.get('product_id')
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Vérifier la disponibilité
        if not product.is_available_in_size(size):
            messages.error(request, f"La taille {size} n'est pas disponible pour ce produit.")
            return redirect('products:product_detail', slug=product.slug)
        
        if quantity > product.get_stock_for_size(size):
            messages.error(request, f"Stock insuffisant pour la taille {size}.")
            return redirect('products:product_detail', slug=product.slug)
        
        cart = Cart(request)
        cart_item = cart.add(product=product, size=size, quantity=quantity)
        
        # Traiter les personnalisations
        customizations = []
        index = 0
        while f'customization_{index}_type' in request.POST:
            custom_type = request.POST.get(f'customization_{index}_type')
            
            if custom_type == 'name':
                custom_name = request.POST.get(f'customization_{index}_name', '')
                custom_number = request.POST.get(f'customization_{index}_number', '')
                custom_price = float(request.POST.get(f'customization_{index}_price', 0))
                
                if custom_name or custom_number:
                    customizations.append({
                        'type': 'name',
                        'name': custom_name,
                        'number': custom_number,
                        'price': custom_price
                    })
            
            elif custom_type == 'badge':
                badge_type = request.POST.get(f'customization_{index}_badge_type', '')
                custom_price = float(request.POST.get(f'customization_{index}_price', 500))
                
                if badge_type:
                    customizations.append({
                        'type': 'badge',
                        'badge_type': badge_type,
                        'price': custom_price
                    })
            
            index += 1
        
        # Ajouter les personnalisations au cart_item
        if customizations and cart_item:
            from products.models import JerseyCustomization, CartItemCustomization
            
            for custom in customizations:
                if custom['type'] == 'name':
                    # Créer ou récupérer l'option de personnalisation nom/numéro
                    customization = JerseyCustomization.get_or_create_name_customization()
                    
                    # Créer la personnalisation pour cet article
                    custom_text = f"{custom['name']} {custom['number']}".strip()
                    CartItemCustomization.objects.create(
                        cart_item=cart_item,
                        customization=customization,
                        custom_text=custom_text,
                        price=custom['price']
                    )
                
                elif custom['type'] == 'badge':
                    # Créer ou récupérer l'option de personnalisation badge
                    customization = JerseyCustomization.get_or_create_badge_customization(custom['badge_type'])
                    
                    # Créer la personnalisation pour cet article
                    CartItemCustomization.objects.create(
                        cart_item=cart_item,
                        customization=customization,
                        price=custom['price']
                    )
        
        # Message de succès
        if customizations:
            messages.success(request, f"{product.name} ({size}) avec personnalisations ajouté au panier.")
        else:
            messages.success(request, f"{product.name} ({size}) ajouté au panier.")
        
        # Rediriger vers la page précédente ou le panier
        next_url = request.POST.get('next', 'cart:cart_detail')
        return redirect(next_url)
        
    except (ValueError, TypeError):
        messages.error(request, "Données invalides.")
        return redirect('products:product_list')


@require_POST
def cart_update(request):
    """Mettre à jour la quantité d'un produit dans le panier"""
    product_id = request.POST.get('product_id')
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 0))
    
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = Cart(request)
        
        if quantity > 0:
            # Vérifier le stock
            if quantity > product.get_stock_for_size(size):
                messages.error(request, f"Stock insuffisant pour la taille {size}.")
                return redirect('cart:cart_detail')
            
            cart.update_quantity(product=product, size=size, quantity=quantity)
            messages.success(request, f"Quantité mise à jour pour {product.name} ({size}).")
        else:
            cart.remove(product=product, size=size)
            messages.success(request, f"{product.name} ({size}) retiré du panier.")
        
        return redirect('cart:cart_detail')
        
    except (ValueError, TypeError):
        messages.error(request, "Données invalides.")
        return redirect('cart:cart_detail')


@require_POST
def cart_remove(request):
    """Retirer un produit du panier"""
    product_id = request.POST.get('product_id')
    size = request.POST.get('size')
    
    try:
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        cart.remove(product=product, size=size)
        messages.success(request, f"{product.name} ({size}) retiré du panier.")
        
        return redirect('cart:cart_detail')
        
    except (ValueError, TypeError):
        messages.error(request, "Données invalides.")
        return redirect('cart:cart_detail')


def cart_clear(request):
    """Vider le panier"""
    cart = Cart(request)
    cart.clear()
    messages.success(request, "Votre panier a été vidé.")
    return redirect('cart:cart_detail')


# Vue AJAX pour mettre à jour le panier sans recharger la page
@require_POST
def cart_update_ajax(request):
    """Mettre à jour le panier via AJAX"""
    product_id = request.POST.get('product_id')
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 0))
    
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = Cart(request)
        
        if quantity > 0:
            if quantity > product.get_stock_for_size(size):
                return JsonResponse({
                    'success': False,
                    'message': f"Stock insuffisant pour la taille {size}."
                })
            
            cart.update_quantity(product=product, size=size, quantity=quantity)
        else:
            cart.remove(product=product, size=size)
        
        return JsonResponse({
            'success': True,
            'cart_total': len(cart),
            'cart_total_price': float(cart.get_total_price()),
            'message': 'Panier mis à jour avec succès.'
        })
        
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'message': 'Données invalides.'
        })
