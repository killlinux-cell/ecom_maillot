#!/usr/bin/env python
"""
Script de diagnostic des fichiers statiques sur le VPS
Vérifie l'état des fichiers collectés et la configuration
"""

import os
import subprocess
import sys

def check_static_files():
    """Vérifie l'état des fichiers statiques"""
    
    print("🔍 Diagnostic des Fichiers Statiques sur le VPS")
    print("=" * 60)
    
    # Vérifier les dossiers
    static_dirs = [
        'staticfiles',
        'static',
        'media',
        'staticfiles/admin',
        'staticfiles/dashboard'
    ]
    
    print("\n📁 Vérification des dossiers:")
    for dir_path in static_dirs:
        if os.path.exists(dir_path):
            file_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
            size = sum(os.path.getsize(os.path.join(dir_path, f)) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)))
            print(f"✅ {dir_path:25} - {file_count} fichiers - {size/1024/1024:.2f} MB")
        else:
            print(f"❌ {dir_path:25} - N'existe pas")
    
    # Vérifier la configuration Django
    print("\n⚙️  Configuration Django:")
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_maillot.settings')
        django.setup()
        
        from django.conf import settings
        
        print(f"STATIC_URL: {getattr(settings, 'STATIC_URL', 'Non défini')}")
        print(f"STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Non défini')}")
        print(f"STATICFILES_STORAGE: {getattr(settings, 'STATICFILES_STORAGE', 'Non défini')}")
        print(f"DEBUG: {getattr(settings, 'DEBUG', 'Non défini')}")
        
    except Exception as e:
        print(f"❌ Erreur Django: {e}")

def check_nginx_config():
    """Vérifie la configuration Nginx"""
    
    print("\n🌐 Configuration Nginx:")
    
    nginx_configs = [
        '/etc/nginx/sites-available/ecom_maillot',
        '/etc/nginx/sites-enabled/ecom_maillot',
        '/etc/nginx/nginx.conf'
    ]
    
    for config_file in nginx_configs:
        if os.path.exists(config_file):
            print(f"✅ {config_file}")
            try:
                with open(config_file, 'r') as f:
                    content = f.read()
                    if 'static' in content.lower():
                        print(f"  📝 Contient des références aux fichiers statiques")
                    if 'location /static/' in content:
                        print(f"  ✅ Configuration /static/ trouvée")
                    if 'location /media/' in content:
                        print(f"  ✅ Configuration /media/ trouvée")
            except Exception as e:
                print(f"  ❌ Erreur lecture: {e}")
        else:
            print(f"❌ {config_file} - N'existe pas")

def check_permissions():
    """Vérifie les permissions des dossiers"""
    
    print("\n🔐 Vérification des permissions:")
    
    dirs_to_check = [
        'staticfiles',
        'static',
        'media',
        '/var/www/ecom_maillot/staticfiles',
        '/var/www/ecom_maillot/media'
    ]
    
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            try:
                stat = os.stat(dir_path)
                mode = oct(stat.st_mode)[-3:]
                owner = stat.st_uid
                print(f"📁 {dir_path:35} - Permissions: {mode} - UID: {owner}")
            except Exception as e:
                print(f"❌ {dir_path:35} - Erreur: {e}")
        else:
            print(f"❌ {dir_path:35} - N'existe pas")

def create_fix_script():
    """Crée un script de correction"""
    
    print("\n📜 Création du script de correction...")
    
    script_content = """#!/bin/bash
# Script de correction des fichiers statiques sur le VPS
# À exécuter sur le serveur de production

echo "🔧 Correction des fichiers statiques..."

# Variables
PROJECT_DIR="/var/www/ecom_maillot"
STATIC_DIR="$PROJECT_DIR/staticfiles"
MEDIA_DIR="$PROJECT_DIR/media"

echo "📁 Vérification des dossiers..."

# Créer les dossiers s'ils n'existent pas
sudo mkdir -p "$STATIC_DIR"
sudo mkdir -p "$MEDIA_DIR"

# Donner les bonnes permissions
echo "🔐 Correction des permissions..."
sudo chown -R www-data:www-data "$PROJECT_DIR"
sudo chmod -R 755 "$PROJECT_DIR"

# Vérifier que collectstatic a été exécuté
if [ ! -d "$STATIC_DIR/admin" ]; then
    echo "⚠️  collectstatic n'a pas été exécuté correctement"
    echo "🔄 Exécution de collectstatic..."
    cd "$PROJECT_DIR"
    source venv/bin/activate
    python manage.py collectstatic --noinput
fi

# Vérifier la configuration Nginx
echo "🌐 Vérification de la configuration Nginx..."

NGINX_CONFIG="/etc/nginx/sites-available/ecom_macom_maillot"

if [ -f "$NGINX_CONFIG" ]; then
    echo "✅ Configuration Nginx trouvée"
    
    # Vérifier si la configuration contient les bonnes directives
    if ! grep -q "location /static/" "$NGINX_CONFIG"; then
        echo "⚠️  Configuration /static/ manquante dans Nginx"
        echo "📝 Ajout de la configuration..."
        
        # Créer une sauvegarde
        sudo cp "$NGINX_CONFIG" "$NGINX_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
        
        # Ajouter la configuration des fichiers statiques
        sudo tee -a "$NGINX_CONFIG" > /dev/null << 'EOF'

# Configuration des fichiers statiques
location /static/ {
    alias /var/www/ecom_maillot/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /var/www/ecom_maillot/media/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
EOF
        
        echo "✅ Configuration ajoutée"
    else
        echo "✅ Configuration /static/ déjà présente"
    fi
    
    if ! grep -q "location /media/" "$NGINX_CONFIG"; then
        echo "⚠️  Configuration /media/ manquante dans Nginx"
    else
        echo "✅ Configuration /media/ déjà présente"
    fi
else
    echo "❌ Configuration Nginx non trouvée"
fi

# Redémarrer Nginx
echo "🔄 Redémarrage de Nginx..."
sudo systemctl restart nginx

# Vérifier le statut
echo "📊 Vérification finale..."
echo "📁 Fichiers statiques: $(find $STATIC_DIR -type f | wc -l)"
echo "📁 Fichiers médias: $(find $MEDIA_DIR -type f | wc -l)"

echo "🎉 Correction terminée!"
echo "🌐 Testez maintenant: http://votre-domaine.com/static/admin/css/base.css"
"""
    
    script_file = 'fix_static_vps.sh'
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Rendre exécutable
    if os.name != 'nt':
        os.chmod(script_file, 0o755)
    
    print(f"✅ Script de correction créé: {script_file}")
    return script_file

def main():
    """Fonction principale"""
    
    print("🚨 Diagnostic des Fichiers Statiques sur le VPS")
    print("=" * 60)
    
    # 1. Vérifier les fichiers statiques
    check_static_files()
    
    # 2. Vérifier la configuration Nginx
    check_nginx_config()
    
    # 3. Vérifier les permissions
    check_permissions()
    
    # 4. Créer le script de correction
    fix_script = create_fix_script()
    
    print("\n" + "=" * 60)
    print("🔧 SOLUTIONS RECOMMANDÉES")
    print("=" * 60)
    print("1. Exécuter le script de correction: ./fix_static_vps.sh")
    print("2. Vérifier que collectstatic a été exécuté")
    print("3. Vérifier la configuration Nginx")
    print("4. Redémarrer Nginx")
    print("\n📋 Vérifications à faire:")
    print("- Les fichiers sont-ils dans /var/www/ecom_maillot/staticfiles/ ?")
    print("- Nginx est-il configuré pour servir /static/ et /media/ ?")
    print("- Les permissions sont-elles correctes ?")
    print("\n✅ Utilisez le script de correction pour résoudre le problème!")

if __name__ == '__main__':
    main()

