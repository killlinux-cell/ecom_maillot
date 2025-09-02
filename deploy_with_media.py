#!/usr/bin/env python
"""
Script de déploiement complet avec conservation des médias
Gère automatiquement la sauvegarde et la restauration des images
"""

import os
import shutil
import zipfile
import subprocess
import sys
from datetime import datetime

def check_git_status():
    """Vérifie le statut Git et demande confirmation"""
    
    print("🔍 Vérification du statut Git...")
    
    try:
        # Vérifier s'il y a des modifications non commitées
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️  ATTENTION: Il y a des modifications non commitées!")
            print("📝 Modifications détectées:")
            for line in result.stdout.strip().split('\n'):
                if line:
                    print(f"  {line}")
            
            response = input("\n❓ Voulez-vous continuer le déploiement? (oui/non): ")
            if response.lower() not in ['oui', 'o', 'yes', 'y']:
                print("❌ Déploiement annulé")
                sys.exit(1)
        else:
            print("✅ Aucune modification non commitée détectée")
            
    except subprocess.CalledProcessError:
        print("⚠️  Impossible de vérifier le statut Git")
        response = input("❓ Continuer quand même? (oui/non): ")
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            sys.exit(1)

def backup_media():
    """Sauvegarde les médias avant déploiement"""
    
    print("\n💾 Sauvegarde des médias...")
    
    media_dir = 'media'
    if not os.path.exists(media_dir):
        print("⚠️  Aucun dossier media trouvé")
        return None
    
    # Créer le dossier de sauvegarde
    backup_dir = 'deployment_backup'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Nom du fichier de sauvegarde
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'media_backup_{timestamp}.zip'
    backup_path = os.path.join(backup_dir, backup_file)
    
    # Créer l'archive
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, media_dir)
                zipf.write(file_path, arcname)
                print(f"  ✅ Sauvegardé: {arcname}")
    
    print(f"✅ Sauvegarde créée: {backup_path}")
    return backup_path

def create_production_media_script(backup_path):
    """Crée un script pour restaurer les médias en production"""
    
    print("\n📜 Création du script de restauration...")
    
    script_content = f"""#!/bin/bash
# Script de restauration des médias en production
# Généré automatiquement le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "🖼️  Restauration des médias en production..."

# Variables
MEDIA_DIR="/var/www/ecom_maillot/media"
BACKUP_FILE="{os.path.basename(backup_path)}"

# Vérifier que le fichier de sauvegarde existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Fichier de sauvegarde non trouvé: $BACKUP_FILE"
    exit 1
fi

# Créer le dossier des médias s'il n'existe pas
sudo mkdir -p "$MEDIA_DIR"

# Donner les bonnes permissions
sudo chown -R www-data:www-data "$MEDIA_DIR"
sudo chmod -R 755 "$MEDIA_DIR"

# Sauvegarder les médias existants (sécurité)
if [ -d "$MEDIA_DIR" ] && [ "$(ls -A $MEDIA_DIR)" ]; then
    echo "🔄 Sauvegarde des médias existants..."
    sudo cp -r "$MEDIA_DIR" "$MEDIA_DIR.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Extraire la nouvelle sauvegarde
echo "📦 Extraction des médias..."
sudo unzip -o "$BACKUP_FILE" -d "$MEDIA_DIR"

# Corriger les permissions
echo "🔧 Correction des permissions..."
sudo chown -R www-data:www-data "$MEDIA_DIR"
sudo chmod -R 755 "$MEDIA_DIR"

# Vérifier la restauration
echo "✅ Vérification de la restauration..."
FILE_COUNT=$(find "$MEDIA_DIR" -type f | wc -l)
echo "📁 Nombre de fichiers restaurés: $FILE_COUNT"

echo "🎉 Restauration terminée avec succès!"
echo "🔄 Redémarrage des services..."

# Redémarrer les services web
sudo systemctl restart nginx
sudo systemctl restart gunicorn

echo "🚀 Services redémarrés!"
"""
    
    script_file = 'restore_media_production.sh'
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Rendre exécutable sur Unix/Linux
    if os.name != 'nt':
        os.chmod(script_file, 0o755)
    
    print(f"✅ Script créé: {script_file}")
    return script_file

def create_deployment_checklist():
    """Crée une checklist de déploiement"""
    
    print("\n📋 Création de la checklist de déploiement...")
    
    checklist_content = f"""# 📋 Checklist de Déploiement - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🚀 ÉTAPES DE DÉPLOIEMENT

### 1. Préparation (Développement)
- [x] Sauvegarde des médias créée
- [x] Script de restauration généré
- [x] Vérification Git effectuée

### 2. Transfert vers la Production
- [ ] Transférer le fichier de sauvegarde: {os.path.basename(backup_path) if 'backup_path' in locals() else 'media_backup_*.zip'}
- [ ] Transférer le script de restauration: restore_media_production.sh
- [ ] Transférer le code source (git pull)

### 3. Restauration des Médias (Production)
```bash
# Sur le serveur de production
chmod +x restore_media_production.sh
./restore_media_production.sh
```

### 4. Vérifications Post-Déploiement
- [ ] Vérifier que toutes les images s'affichent
- [ ] Tester l'upload de nouvelles images
- [ ] Vérifier les permissions des dossiers
- [ ] Tester la navigation du dashboard

### 5. Services
- [ ] Nginx redémarré
- [ ] Gunicorn redémarré
- [ ] Base de données synchronisée

## 📁 FICHIERS IMPORTANTS
- Sauvegarde des médias: {os.path.basename(backup_path) if 'backup_path' in locals() else 'media_backup_*.zip'}
- Script de restauration: restore_media_production.sh
- Checklist: DEPLOYMENT_CHECKLIST.md

## ⚠️  NOTES IMPORTANTES
- Toujours sauvegarder avant de déployer
- Vérifier les permissions des dossiers media
- Tester l'affichage des images après déploiement
- Garder une copie de la sauvegarde en local

## 🆘 EN CAS DE PROBLÈME
1. Vérifier les logs: `sudo journalctl -u nginx -u gunicorn`
2. Vérifier les permissions: `ls -la /var/www/ecom_maillot/media`
3. Restaurer depuis la sauvegarde de sécurité
4. Contacter l'administrateur système

---
*Checklist générée automatiquement le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    checklist_file = 'DEPLOYMENT_CHECKLIST.md'
    with open(checklist_file, 'w', encoding='utf-8') as f:
        f.write(checklist_content)
    
    print(f"✅ Checklist créée: {checklist_file}")
    return checklist_file

def main():
    """Fonction principale"""
    
    print("🚀 Déploiement Complet avec Conservation des Médias")
    print("=" * 60)
    
    # 1. Vérification Git
    check_git_status()
    
    # 2. Sauvegarde des médias
    backup_path = backup_media()
    
    # 3. Script de restauration
    restore_script = create_production_media_script(backup_path)
    
    # 4. Checklist de déploiement
    checklist = create_deployment_checklist()
    
    print("\n" + "=" * 60)
    print("🎉 PRÉPARATION TERMINÉE!")
    print("=" * 60)
    print(f"💾 Sauvegarde: {backup_path}")
    print(f"📜 Script de restauration: {restore_script}")
    print(f"📋 Checklist: {checklist}")
    
    print("\n🚀 PROCHAINES ÉTAPES:")
    print("1. Transférer ces fichiers sur votre serveur de production")
    print("2. Exécuter le script de restauration")
    print("3. Suivre la checklist de déploiement")
    print("\n✅ Vos images sont maintenant protégées et prêtes pour la production!")

if __name__ == '__main__':
    main()
