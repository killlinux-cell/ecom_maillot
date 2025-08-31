from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import json
import requests
from .models import Payment, PaymentLog
from orders.models import Order



@login_required
def process_payment(request, order_id):
    """Traiter le paiement via PayDunya"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        messages.info(request, "Cette commande a déjà été payée.")
        return redirect('orders:order_detail', order_id=order.id)
    
    # Créer ou récupérer le paiement
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'payment_id': f"PAY_{order.order_number}",
            'amount': order.total,
            'customer_name': f"{order.user.first_name} {order.user.last_name}",
            'customer_email': order.user.email,
            'customer_phone': order.shipping_address.phone if order.shipping_address else '',
        }
    )
    
    # Configuration PayDunya
    paydunya_config = {
        'master_key': settings.PAYDUNYA_MASTER_KEY,
        'public_key': settings.PAYDUNYA_PUBLIC_KEY,
        'private_key': settings.PAYDUNYA_PRIVATE_KEY,
        'token': settings.PAYDUNYA_TOKEN,
        'mode': settings.PAYDUNYA_MODE,
    }
    
    # Préparer les données pour PayDunya
    store_data = {
        "name": "Maillots de Football",
        "tagline": "Les meilleurs maillots de football",
        "postal_address": "Abidjan, Côte d'Ivoire",
        "phone": "+225 0123456789",
        "website_url": "https://maillots-football.ci",
        "logo_url": "https://via.placeholder.com/150x50/28a745/ffffff?text=Maillots"
    }
    
    items = []
    for item in order.items.all():
        items.append({
            "name": item.product_name,
            "quantity": item.quantity,
            "unit_price": float(item.price),
            "total_price": float(item.total_price),
            "description": f"Taille: {item.size}"
        })
    
    payment_data = {
        "invoice": {
            "items": items,
            "total_amount": float(order.total),
            "description": f"Commande {order.order_number}"
        },
        "store": store_data,
        "actions": {
            "callback_url": f"{request.scheme}://{request.get_host()}/payments/webhook/",
            "cancel_url": f"{request.scheme}://{request.get_host()}/payments/cancel/",
            "return_url": f"{request.scheme}://{request.get_host()}/payments/success/"
        },
        "custom_data": {
            "order_id": order.id,
            "payment_id": payment.payment_id
        }
    }
    
    try:
        # Configuration de l'API PayDunya DMP
        api_url = "https://app.paydunya.com/api/v1/dmp-api"
        
        # Headers requis selon la documentation PayDunya
        headers = {
            'Content-Type': 'application/json',
            'PAYDUNYA-MASTER-KEY': paydunya_config['master_key'],
            'PAYDUNYA-PRIVATE-KEY': paydunya_config['private_key'],
            'PAYDUNYA-TOKEN': paydunya_config['token']
        }
        
        # Données selon le format PayDunya DMP
        paydunya_data = {
            "recipient_email": order.user.email,
            "recipient_phone": order.shipping_address.phone if order.shipping_address else None,
            "amount": int(float(order.total)),  # Montant en entier selon la doc
            "support_fees": 1,  # 1 = vous supportez les frais
            "send_notification": 1  # 1 = PayDunya envoie les notifications
        }
        
        # Mode test - simulation du paiement (pour éviter les erreurs PayDunya)
        if paydunya_config['mode'] == 'test' and not paydunya_config['master_key'].startswith('live_'):
            # Simulation pour les tests
            payment.paydunya_token = f"TEST_TOKEN_{payment.payment_id}"
            payment.save()
            
            PaymentLog.objects.create(
                payment=payment,
                event='payment_initiated',
                message='Paiement simulé en mode test',
                data={'mode': 'simulation'}
            )
            
            messages.success(request, "Mode test activé - Paiement simulé avec succès !")
            return redirect(f'/payments/success/?token={payment.paydunya_token}')
        
        # Appel à l'API PayDunya DMP
        print(f"PayDunya Config: {paydunya_config}")
        print(f"PayDunya Data: {paydunya_data}")
        
        response = requests.post(api_url, headers=headers, json=paydunya_data)
        response_data = response.json()
        
        print(f"PayDunya Response: {response_data}")
        
        PaymentLog.objects.create(
            payment=payment,
            event='api_call',
            message=f'Appel API PayDunya DMP',
            data={'request': paydunya_data, 'response': response_data}
        )
        
        # Vérifier la réponse selon la documentation
        if response_data.get('response-code') == '00':
            # Succès - PayDunya a créé la demande de paiement
            reference_number = response_data.get('reference_number')
            payment_url = response_data.get('url')
            
            payment.paydunya_token = reference_number
            payment.paydunya_reference = reference_number
            payment.save()
            
            PaymentLog.objects.create(
                payment=payment,
                event='payment_created',
                message=f'Demande de paiement créée avec succès',
                data={'reference': reference_number, 'url': payment_url}
            )
            
            # Rediriger vers la page de paiement PayDunya
            if payment_url and payment_url.startswith('http'):
                return redirect(payment_url)
            else:
                messages.error(request, "URL de paiement invalide reçue de PayDunya")
                return redirect('orders:order_detail', order_id=order.id)
        
        elif response_data.get('response-code') == '4001':
            # Erreur de mode - doit être en LIVE
            PaymentLog.objects.create(
                payment=payment,
                event='error',
                message='Mode d\'intégration doit être LIVE',
                data={'error': response_data}
            )
            
            # Fallback vers simulation en mode test
            if paydunya_config['mode'] == 'test':
                payment.paydunya_token = f"TEST_TOKEN_{payment.payment_id}"
                payment.save()
                messages.success(request, "Mode test - Paiement simulé avec succès !")
                return redirect(f'/payments/success/?token={payment.paydunya_token}')
            else:
                messages.error(request, "Erreur PayDunya: Mode d'intégration doit être LIVE")
                return redirect('orders:order_detail', order_id=order.id)
        
        else:
            # Autres erreurs
            error_message = response_data.get('message', 'Erreur inconnue PayDunya')
            PaymentLog.objects.create(
                payment=payment,
                event='error',
                message=f'Erreur PayDunya: {error_message}',
                data={'error': response_data}
            )
            
            messages.error(request, f"Erreur lors de l'initialisation du paiement: {error_message}")
            return redirect('orders:order_detail', order_id=order.id)
            
    except Exception as e:
        # Log de l'exception
        PaymentLog.objects.create(
            payment=payment,
            event='payment_error',
            message=f'Erreur: {str(e)}',
            data={}
        )
        
        print(f"Exception PayDunya: {str(e)}")
        messages.error(request, f"Erreur lors du traitement du paiement: {str(e)}")
        return redirect('orders:order_detail', order_id=order.id)


def payment_success(request):
    """Page de succès du paiement"""
    token = request.GET.get('token')
    
    if token:
        try:
            payment = Payment.objects.get(paydunya_token=token)
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Mettre à jour le statut de la commande
            order = payment.order
            order.payment_status = 'paid'
            order.paid_at = timezone.now()
            order.save()
            
            # Log du succès
            PaymentLog.objects.create(
                payment=payment,
                event='payment_success',
                message='Paiement réussi',
                data={'token': token}
            )
            
            messages.success(request, "Paiement effectué avec succès !")
            return redirect('orders:order_detail', order_id=order.id)
            
        except Payment.DoesNotExist:
            messages.error(request, "Paiement introuvable.")
    
    return redirect('products:home')


def payment_cancel(request):
    """Page d'annulation du paiement"""
    messages.warning(request, "Paiement annulé.")
    return redirect('cart:cart_detail')


@login_required
def wave_direct_payment(request, order_id):
    """Paiement direct via Wave"""
    # Permettre aux administrateurs d'accéder aux paiements de toutes les commandes
    if request.user.is_staff or request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
    else:
        # Les utilisateurs normaux ne peuvent accéder qu'à leurs propres commandes
        order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        messages.info(request, "Cette commande a déjà été payée.")
        return redirect('orders:order_detail', order_id=order.id)
    
    # Créer ou récupérer le paiement
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'payment_id': f"WAVE_{order.order_number}",
            'amount': order.total,
            'customer_name': f"{order.user.first_name} {order.user.last_name}",
            'customer_email': order.user.email,
            'customer_phone': order.shipping_address.phone if order.shipping_address else '',
            'payment_method': 'wave_direct',
            'wave_phone_number': settings.WAVE_PHONE_NUMBER,
        }
    )
    
    # Générer un code de paiement unique
    import uuid
    payment.wave_payment_code = f"WAVE_{uuid.uuid4().hex[:8].upper()}"
    payment.save()
    
    # Log du paiement Wave
    PaymentLog.objects.create(
        payment=payment,
        event='wave_payment_initiated',
        message='Paiement Wave direct initié',
        data={'wave_phone': settings.WAVE_PHONE_NUMBER, 'code': payment.wave_payment_code}
    )
    
    context = {
        'order': order,
        'payment': payment,
        'wave_phone': settings.WAVE_PHONE_NUMBER,
        'payment_code': payment.wave_payment_code,
    }
    
    return render(request, 'payments/wave_direct_payment.html', context)








@login_required
def submit_wave_transaction(request, order_id):
    """Soumettre l'ID de transaction Wave pour validation"""
    # Permettre aux administrateurs d'accéder aux paiements de toutes les commandes
    if request.user.is_staff or request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
    else:
        # Les utilisateurs normaux ne peuvent accéder qu'à leurs propres commandes
        order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method != 'POST':
        return redirect('payments:wave_direct_payment', order_id=order.id)
    
    transaction_id = request.POST.get('transaction_id', '').strip()
    customer_phone = request.POST.get('customer_phone', '').strip()
    
    # Validation des données
    if not transaction_id:
        messages.error(request, "L'ID de transaction est requis.")
        return redirect('payments:wave_direct_payment', order_id=order.id)
    
    if not customer_phone:
        messages.error(request, "Le numéro de téléphone est requis.")
        return redirect('payments:wave_direct_payment', order_id=order.id)
    
    # Validation du format de l'ID de transaction (lettres et chiffres uniquement)
    import re
    if not re.match(r'^[A-Za-z0-9]+$', transaction_id):
        messages.error(request, "L'ID de transaction contient des caractères invalides.")
        return redirect('payments:wave_direct_payment', order_id=order.id)
    
    try:
        payment = Payment.objects.get(order=order, payment_method='wave_direct')
        
        # Sauvegarder l'ID de transaction et le numéro de téléphone
        payment.wave_transaction_id = transaction_id
        payment.customer_phone = customer_phone
        payment.status = 'pending'  # En attente de validation par l'admin
        payment.save()
        
        # Log de la soumission
        PaymentLog.objects.create(
            payment=payment,
            event='wave_transaction_submitted',
            message=f'ID de transaction Wave soumis: {transaction_id}',
            data={
                'transaction_id': transaction_id,
                'customer_phone': customer_phone,
                'submitted_by': request.user.username
            }
        )
        
        messages.success(request, 
            "Votre ID de transaction a été soumis avec succès ! "
            "Notre équipe va vérifier le paiement et valider votre commande dans les plus brefs délais. "
            "Vous recevrez une notification par email une fois le paiement confirmé."
        )
        
        # TODO: Envoyer un email de notification à l'admin
        # TODO: Envoyer un email de confirmation au client
        
        return redirect('orders:order_detail', order_id=order.id)
        
    except Payment.DoesNotExist:
        messages.error(request, "Paiement introuvable.")
        return redirect('orders:order_detail', order_id=order.id)


@login_required
def confirm_wave_payment(request, order_id):
    """Confirmer le paiement Wave (manuellement) - Pour l'admin uniquement"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    try:
        payment = Payment.objects.get(order=order, payment_method='wave_direct')
        
        # Marquer le paiement comme terminé
        payment.status = 'completed'
        payment.completed_at = timezone.now()
        payment.save()
        
        # Mettre à jour le statut de la commande
        order.payment_status = 'paid'
        order.paid_at = timezone.now()
        order.save()
        
        # Log de la confirmation
        PaymentLog.objects.create(
            payment=payment,
            event='wave_payment_confirmed',
            message='Paiement Wave confirmé manuellement',
            data={'confirmed_by': request.user.username}
        )
        
        messages.success(request, "Paiement Wave confirmé avec succès !")
        return redirect('orders:order_detail', order_id=order.id)
        
    except Payment.DoesNotExist:
        messages.error(request, "Paiement introuvable.")
        return redirect('orders:order_detail', order_id=order.id)


@csrf_exempt
def payment_webhook(request):
    """Webhook PayDunya pour les notifications de paiement"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Vérifier la signature PayDunya (à implémenter selon la documentation)
            
            token = data.get('token')
            status = data.get('status')
            
            if token:
                try:
                    payment = Payment.objects.get(paydunya_token=token)
                    
                    if status == 'completed':
                        payment.status = 'completed'
                        payment.completed_at = timezone.now()
                        payment.save()
                        
                        # Mettre à jour le statut de la commande
                        order = payment.order
                        order.payment_status = 'paid'
                        order.paid_at = timezone.now()
                        order.save()
                        
                        # Log du webhook
                        PaymentLog.objects.create(
                            payment=payment,
                            event='webhook_received',
                            message='Webhook PayDunya reçu - Paiement confirmé',
                            data=data
                        )
                    
                    elif status == 'failed':
                        payment.status = 'failed'
                        payment.save()
                        
                        # Log de l'échec
                        PaymentLog.objects.create(
                            payment=payment,
                            event='webhook_received',
                            message='Webhook PayDunya reçu - Paiement échoué',
                            data=data
                        )
                    
                except Payment.DoesNotExist:
                    pass
            
            return HttpResponse('OK')
            
        except json.JSONDecodeError:
            return HttpResponse('Invalid JSON', status=400)
    
    return HttpResponse('Method not allowed', status=405)
