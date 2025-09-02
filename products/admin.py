from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Team, Product, ProductImage, Review, JerseyCustomization, CartItemCustomization


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'league', 'created_at']
    list_filter = ['country', 'league', 'created_at']
    search_fields = ['name', 'country', 'league']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'category', 'current_price', 'stock_quantity', 'is_featured', 'is_active', 'is_on_sale_display']
    list_filter = ['category', 'team', 'is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'team__name', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'image', 'category', 'team', 'description')
        }),
        ('Prix et stock', {
            'fields': ('price', 'sale_price', 'stock_quantity', 'available_sizes')
        }),
        ('Statut', {
            'fields': ('is_featured', 'is_active')
        }),
    )
    
    def current_price(self, obj):
        return f"{obj.current_price} FCFA"
    current_price.short_description = 'Prix actuel'
    
    def is_on_sale_display(self, obj):
        if obj.is_on_sale:
            return format_html('<span style="color: green;">✓ En promotion</span>')
        return format_html('<span style="color: red;">✗ Normal</span>')
    is_on_sale_display.short_description = 'En promotion'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "Aucune image"
    image_preview.short_description = 'Aperçu'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(JerseyCustomization)
class JerseyCustomizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'customization_type', 'badge_type', 'price', 'is_active']
    list_filter = ['customization_type', 'badge_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'customization_type', 'badge_type', 'description')
        }),
        ('Prix et statut', {
            'fields': ('price', 'is_active')
        }),
    )


@admin.register(CartItemCustomization)
class CartItemCustomizationAdmin(admin.ModelAdmin):
    list_display = ['cart_item', 'customization', 'custom_text', 'price', 'created_at']
    list_filter = ['customization__customization_type', 'created_at']
    search_fields = ['cart_item__product__name', 'custom_text']
    readonly_fields = ['price', 'created_at']
