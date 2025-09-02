#!/usr/bin/env python
"""
Script de sauvegarde et synchronisation des médias pour la production
Conserve toutes les images et fichiers uploadés lors du déploiement
"""

import os
import shutil
import zipfile
from datetime import datetime
import json

def backup_media_files():
    """Sauvegarde tous les fichiers médias"""
    
    # Configuration
    media_dir = 'media'
    backup_dir = 'backups'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Créer le dossier de sauvegarde
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Nom du fichier de sauvegarde
    backup_filename = f'media_backup_{timestamp}.zip'
    backup_path = os.path.join(backup_dir, backup_filename)
    
    print(f"🔄 Sauvegarde des médias en cours...")
    print(f"📁 Dossier source: {media_dir}")
    print(f"💾 Fichier de sauvegarde: {backup_path}")
    
    # Créer l'archive ZIP
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(media_dir):
            for root, dirs, files in os.walk(media_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, media_dir)
                    zipf.write(file_path, arcname)
                    print(f"  ✅ Ajouté: {arcname}")
        else:
            print(f"⚠️  Le dossier {media_dir} n'existe pas encore")
    
    print(f"✅ Sauvegarde terminée: {backup_path}")
    return backup_path

def create_media_inventory():
    """Crée un inventaire détaillé de tous les fichiers médias"""
    
    media_dir = 'media'
    inventory = {
        'timestamp': datetime.now().isoformat(),
        'total_files': 0,
        'total_size': 0,
        'categories': {},
        'files': []
    }
    
    if not os.path.exists(media_dir):
        print(f"⚠️  Le dossier {media_dir} n'existe pas")
        return inventory
    
    print(f"📋 Création de l'inventaire des médias...")
    
    for root, dirs, files in os.walk(media_dir):
        category = os.path.relpath(root, media_dir) if root != media_dir else 'root'
        
        if category not in inventory['categories']:
            inventory['categories'][category] = {
                'file_count': 0,
                'total_size': 0
            }
        
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            
            file_info = {
                'path': os.path.relpath(file_path, media_dir),
                'size': file_size,
                'category': category,
                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }
            
            inventory['files'].append(file_info)
            inventory['categories'][category]['file_count'] += 1
            inventory['categories'][category]['total_size'] += file_size
            inventory['total_files'] += 1
            inventory['total_size'] += file_size
    
    # Sauvegarder l'inventaire
    inventory_file = f'backups/media_inventory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(inventory_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Inventaire créé: {inventory_file}")
    print(f"📁 Total: {inventory['total_files']} fichiers")
    print(f"💾 Taille totale: {inventory['total_size'] / (1024*1024):.2f} MB")
    
    return inventory

def sync_media_to_production(production_path):
    """Synchronise les médias vers le serveur de production"""
    
    media_dir = 'media'
    if not os.path.exists(media_dir):
        print(f"❌ Le dossier {media_dir} n'existe pas")
        return False
    
    print(f"🚀 Synchronisation vers la production...")
    print(f"📁 Source: {media_dir}")
    print(f"🎯 Destination: {production_path}")
    
    try:
        # Copier tous les fichiers
        if os.path.exists(production_path):
            shutil.rmtree(production_path)
        
        shutil.copytree(media_dir, production_path)
        print(f"✅ Synchronisation terminée avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation: {e}")
        return False

def create_deployment_script():
    """Crée un script de déploiement pour la production"""
    
    script_content = """#!/bin/bash
# Script de déploiement des médias pour la production
# À exécuter sur le serveur de production

echo "🚀 Déploiement des médias en cours..."

# Créer le dossier des médias s'il n'existe pas
sudo mkdir -p /var/www/ecom_maillot/media

# Donner les bonnes permissions
sudo chown -R www-data:www-data /var/www/ecom_maillot/media
sudo chmod -R 755 /var/www/ecom_maillot/media

# Copier les médias depuis la sauvegarde
if [ -f "media_backup_latest.zip" ]; then
    echo "📦 Extraction de la sauvegarde des médias..."
    unzip -o media_backup_latest.zip -d /var/www/ecom_maillot/
    echo "✅ Médias déployés avec succès!"
else
    echo "⚠️  Aucune sauvegarde trouvée"
fi

# Redémarrer le serveur web
echo "🔄 Redémarrage du serveur web..."
sudo systemctl restart nginx
sudo systemctl restart gunicorn

echo "🎉 Déploiement terminé!"
"""
    
    script_file = 'deploy_media_production.sh'
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Rendre le script exécutable (sur Unix/Linux)
    if os.name != 'nt':  # Pas Windows
        os.chmod(script_file, 0o755)
    
    print(f"📜 Script de déploiement créé: {script_file}")
    return script_file

def main():
    """Fonction principale"""
    
    print("🖼️  Gestionnaire de Médias pour la Production")
    print("=" * 50)
    
    # 1. Sauvegarde
    backup_path = backup_media_files()
    
    # 2. Inventaire
    inventory = create_media_inventory()
    
    # 3. Script de déploiement
    deploy_script = create_deployment_script()
    
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES ACTIONS")
    print("=" * 50)
    print(f"💾 Sauvegarde créée: {backup_path}")
    print(f"📊 Inventaire créé: {inventory['total_files']} fichiers")
    print(f"📜 Script de déploiement: {deploy_script}")
    print("\n🚀 POUR LA PRODUCTION:")
    print("1. Transférer le fichier de sauvegarde sur le serveur")
    print("2. Exécuter le script de déploiement")
    print("3. Vérifier que tous les médias sont présents")
    print("\n✅ Vos images sont maintenant protégées!")

if __name__ == '__main__':
    main()
