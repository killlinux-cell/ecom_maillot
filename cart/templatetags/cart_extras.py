from django import template
from cart.models import CartItem

register = template.Library()

@register.filter
def get_cart_item(item, user):
    """
    Récupère le cart_item correspondant à un item du panier
    pour accéder aux personnalisations
    """
    try:
        cart_item = CartItem.objects.filter(
            cart__user=user,
            product=item['product'],
            size=item['size']
        ).first()
        return cart_item
    except:
        return None
