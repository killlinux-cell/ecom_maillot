from .cart import Cart


def cart(request):
    """Context processor pour rendre le panier disponible dans tous les templates"""
    return {'cart': Cart(request)}
