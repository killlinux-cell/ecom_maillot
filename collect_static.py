#!/usr/bin/env python
"""
Script pour collecter les fichiers statiques et résoudre le problème de l'admin Django
"""

import os
import sys
import django
from pathlib import Path

# Ajouter le répertoire du projet au path Python
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings

def collect_static():
    """Collecte les fichiers statiques"""
    print("🔄 Collecte des fichiers statiques...")
    
    try:
        # Vérifier que STATIC_ROOT existe
        static_root = Path(settings.STATIC_ROOT)
        if not static_root.exists():
            static_root.mkdir(parents=True, exist_ok=True)
            print(f"✅ Créé le répertoire STATIC_ROOT: {static_root}")
        
        # Collecter les fichiers statiques
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Fichiers statiques collectés avec succès!")
        
        # Vérifier que l'admin Django est bien présent
        admin_static = static_root / 'admin'
        if admin_static.exists():
            print(f"✅ Admin Django trouvé dans: {admin_static}")
            
            # Lister quelques fichiers pour vérification
            admin_files = list(admin_static.rglob('*.css'))[:5]
            if admin_files:
                print("📁 Fichiers CSS de l'admin trouvés:")
                for file in admin_files:
                    print(f"   - {file.relative_to(static_root)}")
            else:
                print("⚠️  Aucun fichier CSS trouvé dans l'admin")
        else:
            print("❌ Répertoire admin non trouvé dans STATIC_ROOT")
            
    except Exception as e:
        print(f"❌ Erreur lors de la collecte: {e}")
        return False
    
    return True

def check_static_files():
    """Vérifie la présence des fichiers statiques essentiels"""
    print("\n🔍 Vérification des fichiers statiques...")
    
    static_root = Path(settings.STATIC_ROOT)
    essential_files = [
        'admin/css/base.css',
        'admin/css/dashboard.css',
        'admin/css/forms.css',
        'admin/js/core.js',
        'admin/js/admin/RelatedObjectLookups.js'
    ]
    
    missing_files = []
    for file_path in essential_files:
        full_path = static_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MANQUANT")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} fichiers essentiels manquants")
        return False
    else:
        print("\n✅ Tous les fichiers essentiels sont présents")
        return True

def fix_permissions():
    """Corrige les permissions des fichiers statiques"""
    print("\n🔧 Correction des permissions...")
    
    static_root = Path(settings.STATIC_ROOT)
    try:
        # Rendre les fichiers lisibles par le serveur web
        for file_path in static_root.rglob('*'):
            if file_path.is_file():
                file_path.chmod(0o644)  # rw-r--r--
            elif file_path.is_dir():
                file_path.chmod(0o755)  # rwxr-xr-x
        
        print("✅ Permissions corrigées")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la correction des permissions: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Script de résolution du problème de l'admin Django")
    print("=" * 60)
    
    # Collecter les fichiers statiques
    if not collect_static():
        print("❌ Échec de la collecte des fichiers statiques")
        return
    
    # Vérifier les fichiers
    if not check_static_files():
        print("❌ Fichiers statiques incomplets")
        return
    
    # Corriger les permissions
    if not fix_permissions():
        print("❌ Échec de la correction des permissions")
        return
    
    print("\n🎉 Problème résolu! L'admin Django devrait maintenant s'afficher correctement.")
    print("\n📋 Actions effectuées:")
    print("   1. Collecte des fichiers statiques")
    print("   2. Vérification de l'intégrité")
    print("   3. Correction des permissions")
    print("\n💡 Si le problème persiste, vérifiez:")
    print("   - La configuration de votre serveur web (nginx/apache)")
    print("   - Les variables d'environnement (DEBUG=False en production)")
    print("   - La configuration WhiteNoise dans settings.py")

if __name__ == '__main__':
    main()
