from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up


@receiver(user_signed_up)
def user_signed_up_handler(sender, request, user, **kwargs):
    """
    Signal pour capturer l'inscription d'un utilisateur
    et ajouter des informations supplémentaires si nécessaire
    """
    # Récupérer les données prénom/nom du formulaire
    first_name = request.POST.get('first_name', '')
    last_name = request.POST.get('last_name', '')
    
    # Mettre à jour l'utilisateur
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    
    user.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Créer automatiquement un profil utilisateur lors de la création d'un utilisateur
    """
    if created:
        # Vous pouvez créer un modèle Profile ici si nécessaire
        pass
