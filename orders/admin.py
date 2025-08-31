from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Address, OrderItemCustomization


class OrderItemCustomizationInline(admin.TabularInline):
    model = OrderItemCustomization
    extra = 0
    readonly_fields = ['price', 'created_at']
    verbose_name = "Personnalisation"
    verbose_name_plural = "Personnalisations"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'price', 'total_price']
    inlines = [OrderItemCustomizationInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'paid_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Informations de commande', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Adresse de livraison', {
            'fields': ('shipping_address',)
        }),
        ('Paiement', {
            'fields': ('payment_method', 'payment_id')
        }),
        ('Totaux', {
            'fields': ('subtotal', 'shipping_cost', 'total')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total(self, obj):
        return f"{obj.total} FCFA"
    total.short_description = 'Total'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'size', 'quantity', 'price', 'total_price', 'customization_count', 'customization_details']
    list_filter = ['size']
    search_fields = ['order__order_number', 'product__name', 'product_name']
    readonly_fields = ['product_name', 'price', 'total_price', 'customization_details']
    inlines = [OrderItemCustomizationInline]
    
    def customization_count(self, obj):
        count = obj.customizations.count()
        if count > 0:
            return format_html('<span style="color: green;">{} perso.</span>', count)
        return format_html('<span style="color: gray;">Aucune</span>')
    customization_count.short_description = 'Personnalisations'
    
    def customization_details(self, obj):
        customizations = obj.customizations.all()
        if not customizations:
            return format_html('<span style="color: gray;">Aucune personnalisation</span>')
        
        details = []
        for custom in customizations:
            if custom.customization.customization_type == 'name' and custom.custom_text:
                details.append(f"Nom: '{custom.custom_text}' (+{custom.price} FCFA)")
            else:
                details.append(f"{custom.customization.name} (+{custom.price} FCFA)")
        
        return format_html('<br>'.join(details))
    customization_details.short_description = 'Détails personnalisations'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'country', 'is_default']
    list_filter = ['country', 'is_default', 'created_at']
    search_fields = ['user__username', 'first_name', 'last_name', 'city']
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Nom complet'


@admin.register(OrderItemCustomization)
class OrderItemCustomizationAdmin(admin.ModelAdmin):
    list_display = ['order_item', 'customization', 'custom_text', 'price', 'created_at']
    list_filter = ['customization__customization_type', 'created_at']
    search_fields = ['order_item__product_name', 'custom_text']
    readonly_fields = ['price', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order_item', 'order_item__order', 'customization'
        )
