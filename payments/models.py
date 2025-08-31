from django.db import models
from orders.models import Order


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', verbose_name="Commande")
    payment_id = models.CharField(max_length=100, unique=True, verbose_name="ID de paiement")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    currency = models.CharField(max_length=3, default='XOF', verbose_name="Devise")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # PayDunya specific fields
    paydunya_token = models.CharField(max_length=100, blank=True, verbose_name="Token PayDunya")
    paydunya_receipt_url = models.URLField(blank=True, verbose_name="URL de reçu PayDunya")
    paydunya_reference = models.CharField(max_length=100, blank=True, verbose_name="Référence PayDunya")
    
    # Wave direct payment fields
    wave_payment_code = models.CharField(max_length=100, blank=True, verbose_name="Code de paiement Wave")
    wave_phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numéro Wave")
    wave_transaction_id = models.CharField(max_length=100, blank=True, verbose_name="ID Transaction Wave")
    payment_method = models.CharField(max_length=20, default='paydunya', choices=[
        ('paydunya', 'PayDunya'),
        ('wave_direct', 'Wave Direct'),
    ], verbose_name="Méthode de paiement")
    
    # Customer information
    customer_name = models.CharField(max_length=200, verbose_name="Nom du client")
    customer_email = models.EmailField(verbose_name="Email du client")
    customer_phone = models.CharField(max_length=20, verbose_name="Téléphone du client")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Terminé le")

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-created_at']

    def __str__(self):
        return f"Paiement {self.payment_id} - {self.order.order_number}"

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def is_failed(self):
        return self.status == 'failed'

    @property
    def is_pending(self):
        return self.status == 'pending'


class PaymentLog(models.Model):
    """Log des événements de paiement pour le debugging"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='logs', verbose_name="Paiement")
    event = models.CharField(max_length=100, verbose_name="Événement")
    message = models.TextField(verbose_name="Message")
    data = models.JSONField(default=dict, verbose_name="Données")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Log de paiement"
        verbose_name_plural = "Logs de paiement"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event} - {self.payment.payment_id}"
