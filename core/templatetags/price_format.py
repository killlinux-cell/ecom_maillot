from django import template
from django.template.defaultfilters import floatformat
from decimal import Decimal

register = template.Library()

@register.filter
def price_format(value):
    """
    Formate un prix selon les standards ivoiriens
    Exemple: 15000.50 -> 15 000,50 FCFA
    """
    if value is None:
        return "0,00 FCFA"
    
    try:
        # Convertir en Decimal pour une manipulation précise
        if isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, (int, float)):
            value = Decimal(str(value))
        
        # Séparer la partie entière et décimale
        integer_part = int(value)
        decimal_part = value - integer_part
        
        # Formater la partie entière avec des espaces pour les milliers
        formatted_integer = "{:,}".format(integer_part).replace(",", " ")
        
        # Formater la partie décimale
        if decimal_part == 0:
            formatted_decimal = "00"
        else:
            # Garder 2 décimales maximum
            formatted_decimal = str(decimal_part).split('.')[1][:2]
            if len(formatted_decimal) == 1:
                formatted_decimal += "0"
        
        # Assembler le prix
        formatted_price = f"{formatted_integer},{formatted_decimal} FCFA"
        
        return formatted_price
        
    except (ValueError, TypeError, AttributeError):
        return "0,00 FCFA"

@register.filter
def price_format_no_currency(value):
    """
    Formate un prix sans la devise
    Exemple: 15000.50 -> 15 000,50
    """
    if value is None:
        return "0,00"
    
    try:
        # Convertir en Decimal pour une manipulation précise
        if isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, (int, float)):
            value = Decimal(str(value))
        
        # Séparer la partie entière et décimale
        integer_part = int(value)
        decimal_part = value - integer_part
        
        # Formater la partie entière avec des espaces pour les milliers
        formatted_integer = "{:,}".format(integer_part).replace(",", " ")
        
        # Formater la partie décimale
        if decimal_part == 0:
            formatted_decimal = "00"
        else:
            # Garder 2 décimales maximum
            formatted_decimal = str(decimal_part).split('.')[1][:2]
            if len(formatted_decimal) == 1:
                formatted_decimal += "0"
        
        # Assembler le prix
        formatted_price = f"{formatted_integer},{formatted_decimal}"
        
        return formatted_price
        
    except (ValueError, TypeError, AttributeError):
        return "0,00"

@register.filter
def price_format_compact(value):
    """
    Formate un prix de manière compacte
    Exemple: 15000.50 -> 15 000,50 FCFA
    """
    if value is None:
        return "0,00 FCFA"
    
    try:
        # Convertir en Decimal pour une manipulation précise
        if isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, (int, float)):
            value = Decimal(str(value))
        
        # Si le prix est un nombre entier
        if value == int(value):
            formatted_integer = "{:,}".format(int(value)).replace(",", " ")
            return f"{formatted_integer} FCFA"
        else:
            # Utiliser le formatage normal
            return price_format(value)
        
    except (ValueError, TypeError, AttributeError):
        return "0,00 FCFA"
