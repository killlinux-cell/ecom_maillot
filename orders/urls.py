from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('list/', views.order_list, name='order_list'),
    path('cancel/<int:order_id>/', views.order_cancel, name='order_cancel'),
    path('address/create/', views.address_create, name='address_create'),
]
