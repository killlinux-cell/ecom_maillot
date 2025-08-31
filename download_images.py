#!/usr/bin/env python
"""
Script pour télécharger des images de maillots de football depuis Unsplash
"""

import os
import sys
import django
import requests
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

from products.models import Product, ProductImage
from django.conf import settings


def download_image_from_unsplash(query, filename):
    """Télécharger une image depuis Unsplash"""
    try:
        # Utiliser l'API Unsplash (gratuite avec limitations)
        # Vous pouvez obtenir une clé API gratuite sur https://unsplash.com/developers
        # Pour ce script, nous utilisons une approche simple avec des images de placeholder
        
        # URL d'une image de maillot de football depuis Unsplash
        image_urls = [
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop",
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop&crop=face",
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop&crop=entropy",
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800&h=600&fit=crop&crop=edges",
        ]
        
        # Choisir une URL aléatoire
        import random
        image_url = random.choice(image_urls)
        
        # Télécharger l'image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        return response.content
    except Exception as e:
        print(f"Erreur lors du téléchargement de l'image: {e}")
        return None


def create_placeholder_image():
    """Créer une image placeholder simple"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Créer une image 800x600 avec un fond blanc
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Ajouter du texte
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text = "Maillot de Football"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (800 - text_width) // 2
        y = (600 - text_height) // 2
        
        draw.text((x, y), text, fill='black', font=font)
        
        # Convertir en bytes
        import io
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        return img_io.getvalue()
    except ImportError:
        print("Pillow n'est pas installé. Utilisation d'une image simple.")
        return None


def add_images_to_products():
    """Ajouter des images aux produits qui n'en ont pas"""
    products_without_images = Product.objects.filter(images__isnull=True).distinct()
    
    print(f"Trouvé {products_without_images.count()} produits sans images")
    
    for i, product in enumerate(products_without_images, 1):
        print(f"Traitement du produit {i}/{products_without_images.count()}: {product.name}")
        
        # Créer 2-4 images par produit
        num_images = 2  # Vous pouvez augmenter ce nombre
        
        for j in range(num_images):
            try:
                # Essayer de télécharger une image
                image_content = download_image_from_unsplash(f"football jersey {product.team.name}", f"{product.slug}_{j}.jpg")
                
                if not image_content:
                    # Créer une image placeholder
                    image_content = create_placeholder_image()
                
                if image_content:
                    # Créer l'objet ProductImage
                    product_image = ProductImage(product=product)
                    
                    # Sauvegarder l'image
                    filename = f"{product.slug}_{j}.jpg"
                    product_image.image.save(filename, ContentFile(image_content), save=True)
                    
                    print(f"  ✓ Image {j+1} ajoutée")
                else:
                    print(f"  ✗ Impossible de créer l'image {j+1}")
                    
            except Exception as e:
                print(f"  ✗ Erreur lors de l'ajout de l'image {j+1}: {e}")
        
        print(f"  Terminé pour {product.name}")
        print()


def main():
    """Fonction principale"""
    print("🖼️  Ajout d'images aux produits")
    print("=" * 50)
    
    # Vérifier si le dossier media existe
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)
        print(f"✓ Dossier media créé: {settings.MEDIA_ROOT}")
    
    # Ajouter des images aux produits
    add_images_to_products()
    
    print("=" * 50)
    print("✅ Processus terminé !")
    print()
    print("📝 Notes:")
    print("- Les images sont des placeholders génériques")
    print("- Pour des vraies images de maillots, vous devrez:")
    print("  1. Obtenir une clé API Unsplash gratuite")
    print("  2. Modifier le script pour utiliser l'API officielle")
    print("  3. Ou télécharger manuellement des images depuis:")
    print("     * https://unsplash.com/s/photos/football-jersey")
    print("     * https://www.freepik.com/search?format=search&query=football%20jersey")
    print("     * https://www.shutterstock.com/search/football+jersey")
    print()
    print("🔗 Accès:")
    print(f"  - Site web: http://localhost:8000")
    print(f"  - Admin: http://localhost:8000/admin")


if __name__ == '__main__':
    main()
