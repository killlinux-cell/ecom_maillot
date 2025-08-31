from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.CustomSignupView.as_view(), name='signup'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]
