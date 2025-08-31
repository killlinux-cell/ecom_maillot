from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem
from products.models import CartItemCustomization


class CartItemCustomizationInline(admin.TabularInline):
    model = CartItemCustomization
    extra = 0
    readonly_fields = ['price', 'created_at']
    verbose_name = "Personnalisation"
    verbose_name_plural = "Personnalisations"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'session_key']
    readonly_fields = ['created_at', 'updated_at']
    
    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Articles'
    
    def total_price(self, obj):
        return f"{obj.total_price} FCFA"
    total_price.short_description = 'Prix total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product', 'size', 'quantity', 'base_price', 'customization_price', 'total_price', 'added_at']
    list_filter = ['size', 'added_at']
    search_fields = ['product__name', 'cart__user__username']
    readonly_fields = ['added_at', 'base_price', 'customization_price', 'total_price']
    inlines = [CartItemCustomizationInline]
    
    def base_price(self, obj):
        return f"{obj.base_price} FCFA"
    base_price.short_description = 'Prix de base'
    
    def customization_price(self, obj):
        return f"{obj.customization_price} FCFA"
    customization_price.short_description = 'Prix personnalisations'
    
    def total_price(self, obj):
        return f"{obj.total_price} FCFA"
    total_price.short_description = 'Prix total'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('cart', 'product', 'size', 'quantity')
        }),
        ('Prix', {
            'fields': ('base_price', 'customization_price', 'total_price'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('added_at',),
            'classes': ('collapse',)
        }),
    )
