from django import template

register = template.Library()

@register.filter
def percentage(value, total):
    """Calcule le pourcentage d'une valeur par rapport au total"""
    try:
        if total and total > 0:
            return round((value / total) * 100, 1)
        return 0
    except (ValueError, TypeError):
        return 0
