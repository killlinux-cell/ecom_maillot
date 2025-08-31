#!/usr/bin/env python
"""
Script pour nettoyer les doublons de JerseyCustomization
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

from products.models import JerseyCustomization
from django.db.models import Count

def clean_duplicates():
    """Nettoyer les doublons de JerseyCustomization"""
    print("🧹 Nettoyage des doublons JerseyCustomization...")
    
    # Identifier les doublons
    duplicates = JerseyCustomization.objects.values(
        'customization_type', 'badge_type', 'name'
    ).annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    print(f"📊 {duplicates.count()} groupes de doublons trouvés")
    
    for duplicate in duplicates:
        print(f"\n🔍 Traitement du groupe: {duplicate}")
        
        # Récupérer tous les objets de ce groupe
        objects = JerseyCustomization.objects.filter(
            customization_type=duplicate['customization_type'],
            badge_type=duplicate['badge_type'],
            name=duplicate['name']
        ).order_by('id')
        
        # Garder le premier et supprimer les autres
        to_keep = objects.first()
        to_delete = objects.exclude(id=to_keep.id)
        
        print(f"   ✅ Garde: {to_keep}")
        print(f"   ❌ Supprime: {to_delete.count()} doublons")
        
        # Supprimer les doublons
        to_delete.delete()
    
    print(f"\n✅ Nettoyage terminé!")
    
    # Vérifier le résultat
    total = JerseyCustomization.objects.count()
    print(f"📈 Total JerseyCustomization après nettoyage: {total}")

if __name__ == '__main__':
    clean_duplicates()
