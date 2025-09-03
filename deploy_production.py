#!/usr/bin/env python
"""
Script de déploiement pour ecom_maillot
Ce script prépare votre projet pour la production
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} terminé avec succès")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}:")
        print(f"Commande: {command}")
        print(f"Erreur: {e.stderr}")
        return False

def main():
    """Fonction principale du script de déploiement"""
    print("🚀 Script de déploiement pour ecom_maillot")
    print("=" * 50)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("manage.py").exists():
        print("❌ Erreur: Ce script doit être exécuté depuis la racine du projet")
        sys.exit(1)
    
    # Créer les dossiers nécessaires
    print("\n📁 Création des dossiers nécessaires...")
    Path("logs").mkdir(exist_ok=True)
    Path("staticfiles").mkdir(exist_ok=True)
    
    # Collecter les fichiers statiques
    if not run_command("python manage.py collectstatic --noinput", "Collecte des fichiers statiques"):
        print("❌ Échec de la collecte des fichiers statiques")
        sys.exit(1)
    
    # Vérifier la configuration
    if not run_command("python manage.py check --deploy", "Vérification de la configuration de production"):
        print("❌ Problèmes détectés dans la configuration de production")
        sys.exit(1)
    
    # Créer un fichier .env de production si il n'existe pas
    if not Path(".env").exists():
        print("\n📝 Création du fichier .env...")
        if Path("env.production.example").exists():
            import shutil
            shutil.copy("env.production.example", ".env")
            print("✅ Fichier .env créé à partir de env.production.example")
            print("⚠️  IMPORTANT: Modifiez le fichier .env avec vos vraies valeurs!")
        else:
            print("⚠️  Fichier env.production.example non trouvé")
    
    print("\n🎉 Déploiement préparé avec succès!")
    print("\n📋 Prochaines étapes:")
    print("1. Modifiez le fichier .env avec vos vraies valeurs")
    print("2. Configurez votre serveur web (Nginx/Apache)")
    print("3. Configurez votre base de données PostgreSQL")
    print("4. Démarrez votre application avec gunicorn")
    print("\n🔧 Commandes utiles:")
    print("- python manage.py migrate")
    print("- python manage.py createsuperuser")
    print("- gunicorn ecom_maillot.wsgi:application")

if __name__ == "__main__":
    main()
