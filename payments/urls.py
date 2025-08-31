from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<int:order_id>/', views.process_payment, name='process_payment'),
    path('wave/<int:order_id>/', views.wave_direct_payment, name='wave_direct_payment'),
    path('wave/submit-transaction/<int:order_id>/', views.submit_wave_transaction, name='submit_wave_transaction'),
    path('wave/confirm/<int:order_id>/', views.confirm_wave_payment, name='confirm_wave_payment'),

    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.payment_webhook, name='payment_webhook'),
]
