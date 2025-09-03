#!/usr/bin/env python
"""
Script de test des images en production
Diagnostique pourquoi les images ne s'affichent pas
"""

import os
import sys
from pathlib import Path
from django.conf import settings
from django.core.management import execute_from_command_line

def check_media_files():
    """Vérifier la structure des fichiers media"""
    print("🔍 Vérification des fichiers media...")
    
    media_root = Path("media")
    if not media_root.exists():
        print("❌ Dossier media non trouvé!")
        return False
    
    print(f"✅ Dossier media trouvé: {media_root.absolute()}")
    
    # Vérifier les sous-dossiers
    subdirs = ['products', 'teams', 'categories']
    for subdir in subdirs:
        subdir_path = media_root / subdir
        if subdir_path.exists():
            files = list(subdir_path.glob('*'))
            print(f"📁 {subdir}: {len(files)} fichiers")
            if files:
                print(f"   Exemples: {[f.name for f in files[:3]]}")
        else:
            print(f"⚠️  {subdir}: dossier non trouvé")
    
    return True

def check_permissions():
    """Vérifier les permissions des fichiers media"""
    print("\n🔐 Vérification des permissions...")
    
    media_root = Path("media")
    if not media_root.exists():
        return False
    
    try:
        # Vérifier les permissions du dossier media
        stat = media_root.stat()
        print(f"Permissions media: {oct(stat.st_mode)[-3:]}")
        
        # Vérifier les permissions des fichiers
        for subdir in ['products', 'teams', 'categories']:
            subdir_path = media_root / subdir
            if subdir_path.exists():
                files = list(subdir_path.glob('*'))[:3]
                for file in files:
                    stat = file.stat()
                    print(f"Permissions {file.name}: {oct(stat.st_mode)[-3:]}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des permissions: {e}")
        return False

def check_urls():
    """Vérifier la configuration des URLs"""
    print("\n🌐 Vérification de la configuration des URLs...")
    
    # Vérifier settings.py
    print("📋 Configuration Django:")
    print(f"   MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'Non défini')}")
    print(f"   MEDIA_ROOT: {getattr(settings, 'MEDIA_ROOT', 'Non défini')}")
    print(f"   STATIC_URL: {getattr(settings, 'STATIC_URL', 'Non défini')}")
    print(f"   STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Non défini')}")
    
    # Vérifier wsgi.py
    wsgi_path = Path("ecom_maillot/wsgi.py")
    if wsgi_path.exists():
        with open(wsgi_path, 'r') as f:
            content = f.read()
            if 'WhiteNoise' in content:
                print("✅ WhiteNoise configuré dans wsgi.py")
                if 'add_files' in content:
                    print("✅ Configuration media ajoutée")
                else:
                    print("⚠️  Configuration media manquante")
            else:
                print("❌ WhiteNoise non configuré dans wsgi.py")
    
    return True

def test_image_access():
    """Tester l'accès aux images"""
    print("\n🖼️  Test d'accès aux images...")
    
    media_root = Path("media")
    if not media_root.exists():
        return False
    
    # Chercher des images de test
    test_images = []
    for subdir in ['products', 'teams', 'categories']:
        subdir_path = media_root / subdir
        if subdir_path.exists():
            images = list(subdir_path.glob('*.jpg')) + list(subdir_path.glob('*.png'))
            test_images.extend(images[:2])
    
    if not test_images:
        print("⚠️  Aucune image trouvée pour les tests")
        return False
    
    print(f"📸 Images de test trouvées: {len(test_images)}")
    
    # Tester l'accès
    for img in test_images[:3]:
        relative_path = img.relative_to(media_root)
        url_path = f"/media/{relative_path}"
        print(f"   Image: {img.name}")
        print(f"   Chemin relatif: {relative_path}")
        print(f"   URL attendue: {url_path}")
        print(f"   Taille: {img.stat().st_size} bytes")
        print()
    
    return True

def generate_nginx_config():
    """Générer une configuration Nginx pour les images"""
    print("\n⚙️  Génération de la configuration Nginx...")
    
    config = f"""server {{
    listen 80;
    server_name orapide.shop www.orapide.shop;
    
    # Configuration des fichiers statiques
    location /static/ {{
        alias {Path.cwd() / 'staticfiles'}/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Configuration des fichiers media (IMAGES DES PRODUITS)
    location /media/ {{
        alias {Path.cwd() / 'media'}/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # Types MIME pour les images
        location ~* \.(jpg|jpeg|png|gif|webp)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header Vary Accept-Encoding;
        }}
    }}
    
    # Proxy vers Gunicorn
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
}}"""
    
    # Sauvegarder la configuration
    with open("nginx_images.conf", "w") as f:
        f.write(config)
    
    print("✅ Configuration Nginx générée: nginx_images.conf")
    return True

def main():
    """Fonction principale"""
    print("🖼️  Diagnostic des images en production")
    print("=" * 50)
    
    # Vérifications
    check_media_files()
    check_permissions()
    check_urls()
    test_image_access()
    generate_nginx_config()
    
    print("\n📋 RÉSUMÉ DES ACTIONS À EFFECTUER:")
    print("1. Copier nginx_images.conf vers /etc/nginx/sites-available/")
    print("2. Redémarrer Nginx: sudo systemctl restart nginx")
    print("3. Redémarrer Django: sudo systemctl restart ecom_maillot")
    print("4. Tester une image: http://orapide.shop/media/products/nom_image.jpg")
    
    print("\n🔍 VÉRIFICATIONS:")
    print("- Les images sont-elles dans le dossier media/ ?")
    print("- Les permissions sont-elles correctes (755) ?")
    print("- Nginx est-il configuré pour servir /media/ ?")
    print("- L'application Django redémarre-t-elle ?")

if __name__ == "__main__":
    main()
