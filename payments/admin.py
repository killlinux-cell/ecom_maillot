from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Payment, PaymentLog


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order', 'amount', 'status', 'payment_method', 'customer_name', 'wave_transaction_id', 'created_at']
    list_filter = ['status', 'payment_method', 'currency', 'created_at', 'wave_transaction_id']
    search_fields = ['payment_id', 'order__order_number', 'customer_name', 'customer_email', 'wave_transaction_id']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    actions = ['validate_wave_payments', 'mark_as_completed', 'mark_as_failed', 'show_wave_pending_transactions']
    
    fieldsets = (
        ('Informations de paiement', {
            'fields': ('order', 'payment_id', 'amount', 'currency', 'status', 'payment_method')
        }),
        ('PayDunya', {
            'fields': ('paydunya_token', 'paydunya_receipt_url', 'paydunya_reference'),
            'classes': ('collapse',)
        }),
        ('Wave Direct', {
            'fields': ('wave_payment_code', 'wave_phone_number', 'wave_transaction_id'),
        }),
        ('Client', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def amount(self, obj):
        return f"{obj.amount} {obj.currency}"
    amount.short_description = 'Montant'
    
    def wave_transaction_id(self, obj):
        if obj.wave_transaction_id:
            return format_html('<span style="color: green; font-weight: bold; background-color: #e8f5e8; padding: 2px 6px; border-radius: 3px;">{}</span>', obj.wave_transaction_id)
        return format_html('<span style="color: red; font-style: italic;">En attente</span>')
    wave_transaction_id.short_description = 'ID Transaction Wave'
    
    def validate_wave_payments(self, request, queryset):
        """Valider les paiements Wave en attente"""
        updated = 0
        for payment in queryset.filter(payment_method='wave_direct', status='pending'):
            if payment.wave_transaction_id:
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.save()
                
                # Mettre à jour le statut de la commande
                order = payment.order
                order.payment_status = 'paid'
                order.paid_at = timezone.now()
                order.save()
                
                # Log de la validation
                PaymentLog.objects.create(
                    payment=payment,
                    event='wave_payment_validated_by_admin',
                    message=f'Paiement Wave validé par l\'admin: {payment.wave_transaction_id}',
                    data={'validated_by': request.user.username}
                )
                
                updated += 1
        
        if updated == 1:
            message = "1 paiement Wave a été validé."
        else:
            message = f"{updated} paiements Wave ont été validés."
        
        self.message_user(request, message)
    validate_wave_payments.short_description = "Valider les paiements Wave sélectionnés"
    
    def mark_as_completed(self, request, queryset):
        """Marquer les paiements comme terminés"""
        updated = queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f"{updated} paiement(s) marqué(s) comme terminé(s).")
    mark_as_completed.short_description = "Marquer comme terminé"
    
    def mark_as_failed(self, request, queryset):
        """Marquer les paiements comme échoués"""
        updated = queryset.update(status='failed')
        self.message_user(request, f"{updated} paiement(s) marqué(s) comme échoué(s).")
    mark_as_failed.short_description = "Marquer comme échoué"
    
    def show_wave_pending_transactions(self, request, queryset):
        """Afficher les paiements Wave en attente d'ID de transaction"""
        pending_wave = queryset.filter(payment_method='wave_direct', wave_transaction_id='')
        if pending_wave.count() > 0:
            message = f"{pending_wave.count()} paiement(s) Wave en attente d'ID de transaction"
            self.message_user(request, message, level='WARNING')
        else:
            self.message_user(request, "Aucun paiement Wave en attente d'ID de transaction")
    show_wave_pending_transactions.short_description = "Voir les paiements Wave en attente"


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['payment', 'event', 'message', 'created_at']
    list_filter = ['event', 'created_at']
    search_fields = ['payment__payment_id', 'event', 'message']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
