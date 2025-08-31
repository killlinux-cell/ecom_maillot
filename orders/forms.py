from django import forms
from .models import Order, Address


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Notes spéciales pour la livraison...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['shipping_address'].queryset = Address.objects.filter(user=user)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'city', 'postal_code', 'country']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Téléphone'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'address': forms.TextInput(attrs={'placeholder': 'Adresse complète'}),
            'city': forms.TextInput(attrs={'placeholder': 'Ville'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Code postal'}),
        }
