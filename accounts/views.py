from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from allauth.account.views import SignupView
from allauth.account.forms import SignupForm
from django import forms


class CustomSignupForm(SignupForm):
    """Formulaire d'inscription personnalisé avec champs supplémentaires"""
    first_name = forms.CharField(
        max_length=30,
        label='Prénom',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre prénom'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        label='Nom',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom'
        })
    )

    def save(self, request):
        user = super().save(request)
        if self.cleaned_data.get('first_name'):
            user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data.get('last_name'):
            user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


class CustomSignupView(SignupView):
    form_class = CustomSignupForm
    template_name = 'account/signup.html'


@login_required
def profile_edit(request):
    """Vue pour éditer le profil utilisateur"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        messages.success(request, 'Profil mis à jour avec succès !')
        return redirect('accounts:profile_edit')
    
    return render(request, 'accounts/profile_edit.html')
