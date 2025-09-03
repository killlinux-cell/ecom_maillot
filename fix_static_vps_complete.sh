#!/bin/bash
# Script de correction complète des fichiers statiques sur le VPS
# À exécuter sur le serveur de production

set -e  # Arrêter en cas d'erreur

echo "🔧 CORRECTION COMPLÈTE DES FICHIERS STATIQUES SUR LE VPS"
echo "=" * 60

# Variables
PROJECT_DIR="/var/www/ecom_maillot"
STATIC_DIR="$PROJECT_DIR/staticfiles"
MEDIA_DIR="$PROJECT_DIR/media"
VENV_DIR="$PROJECT_DIR/venv"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que nous sommes sur le serveur de production
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Le dossier du projet n'existe pas: $PROJECT_DIR"
    print_error "Assurez-vous d'exécuter ce script sur le serveur de production"
    exit 1
fi

print_status "Début de la correction des fichiers statiques..."

# 1. Vérifier et créer les dossiers nécessaires
print_status "📁 Création des dossiers nécessaires..."
sudo mkdir -p "$STATIC_DIR"
sudo mkdir -p "$MEDIA_DIR"
print_success "Dossiers créés"

# 2. Vérifier les permissions
print_status "🔐 Correction des permissions..."
sudo chown -R www-data:www-data "$PROJECT_DIR"
sudo chmod -R 755 "$PROJECT_DIR"
print_success "Permissions corrigées"

# 3. Vérifier l'environnement virtuel
if [ ! -d "$VENV_DIR" ]; then
    print_warning "Environnement virtuel non trouvé: $VENV_DIR"
    print_status "Recherche d'un environnement virtuel..."
    
    # Chercher d'autres emplacements possibles
    if [ -d "$PROJECT_DIR/.venv" ]; then
        VENV_DIR="$PROJECT_DIR/.venv"
        print_success "Environnement virtuel trouvé: $VENV_DIR"
    elif [ -d "$PROJECT_DIR/env" ]; then
        VENV_DIR="$PROJECT_DIR/env"
        print_success "Environnement virtuel trouvé: $VENV_DIR"
    else
        print_error "Aucun environnement virtuel trouvé!"
        print_status "Tentative d'utilisation de Python système..."
        VENV_DIR=""
    fi
fi

# 4. Exécuter collectstatic
print_status "🔄 Exécution de collectstatic..."
cd "$PROJECT_DIR"

if [ -n "$VENV_DIR" ]; then
    print_status "Activation de l'environnement virtuel: $VENV_DIR"
    source "$VENV_DIR/bin/activate"
else
    print_warning "Utilisation de Python système"
fi

# Vérifier si collectstatic a déjà été exécuté
if [ ! -d "$STATIC_DIR/admin" ]; then
    print_warning "collectstatic n'a pas été exécuté correctement"
    print_status "Exécution de collectstatic..."
    
    if python manage.py collectstatic --noinput; then
        print_success "collectstatic exécuté avec succès"
    else
        print_error "Erreur lors de l'exécution de collectstatic"
        exit 1
    fi
else
    print_success "collectstatic déjà exécuté"
fi

# 5. Vérifier la configuration Nginx
print_status "🌐 Vérification de la configuration Nginx..."

# Chercher la configuration Nginx
NGINX_CONFIGS=(
    "/etc/nginx/sites-available/ecom_maillot"
    "/etc/nginx/sites-available/default"
    "/etc/nginx/conf.d/ecom_maillot.conf"
)

NGINX_CONFIG=""
for config in "${NGINX_CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        NGINX_CONFIG="$config"
        print_success "Configuration Nginx trouvée: $config"
        break
    fi
done

if [ -z "$NGINX_CONFIG" ]; then
    print_error "Aucune configuration Nginx trouvée!"
    print_status "Création d'une configuration par défaut..."
    
    # Créer une configuration par défaut
    sudo tee /etc/nginx/sites-available/ecom_maillot > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    
    root /var/www/ecom_maillot;
    
    # Configuration des fichiers statiques
    location /static/ {
        alias /var/www/ecom_maillot/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Configuration des fichiers médias
    location /media/ {
        alias /var/www/ecom_maillot/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Proxy vers Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
    
    NGINX_CONFIG="/etc/nginx/sites-available/ecom_maillot"
    print_success "Configuration Nginx créée: $NGINX_CONFIG"
    
    # Activer le site
    sudo ln -sf "$NGINX_CONFIG" /etc/nginx/sites-enabled/
    print_success "Site activé"
fi

# 6. Vérifier et ajouter la configuration des fichiers statiques
print_status "📝 Vérification de la configuration des fichiers statiques..."

if ! grep -q "location /static/" "$NGINX_CONFIG"; then
    print_warning "Configuration /static/ manquante dans Nginx"
    print_status "Ajout de la configuration..."
    
    # Créer une sauvegarde
    sudo cp "$NGINX_CONFIG" "$NGINX_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    print_success "Sauvegarde créée"
    
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
    
    print_success "Configuration /static/ ajoutée"
else
    print_success "Configuration /static/ déjà présente"
fi

if ! grep -q "location /media/" "$NGINX_CONFIG"; then
    print_warning "Configuration /media/ manquante dans Nginx"
else
    print_success "Configuration /media/ déjà présente"
fi

# 7. Vérifier la syntaxe de Nginx
print_status "🔍 Vérification de la syntaxe Nginx..."
if sudo nginx -t; then
    print_success "Syntaxe Nginx valide"
else
    print_error "Erreur de syntaxe dans la configuration Nginx"
    exit 1
fi

# 8. Redémarrer Nginx
print_status "🔄 Redémarrage de Nginx..."
sudo systemctl restart nginx
print_success "Nginx redémarré"

# 9. Vérification finale
print_status "📊 Vérification finale..."
STATIC_COUNT=$(find "$STATIC_DIR" -type f 2>/dev/null | wc -l || echo "0")
MEDIA_COUNT=$(find "$MEDIA_DIR" -type f 2>/dev/null | wc -l || echo "0")

print_success "📁 Fichiers statiques: $STATIC_COUNT"
print_success "📁 Fichiers médias: $MEDIA_COUNT"

# 10. Test de connectivité
print_status "🌐 Test de connectivité..."
if curl -s -o /dev/null -w "%{http_code}" "http://localhost/static/admin/css/base.css" | grep -q "200"; then
    print_success "Test /static/ réussi"
else
    print_warning "Test /static/ échoué - Vérifiez la configuration"
fi

# 11. Afficher les informations de test
echo ""
echo "🎉 CORRECTION TERMINÉE AVEC SUCCÈS!"
echo "=" * 60
echo "📋 INFORMATIONS IMPORTANTES:"
echo "📁 Dossier des fichiers statiques: $STATIC_DIR"
echo "📁 Dossier des médias: $MEDIA_DIR"
echo "🌐 Configuration Nginx: $NGINX_CONFIG"
echo "📊 Nombre de fichiers statiques: $STATIC_COUNT"
echo "📊 Nombre de fichiers médias: $MEDIA_COUNT"
echo ""
echo "🧪 TESTS À EFFECTUER:"
echo "1. Vérifiez l'admin Django: http://votre-domaine.com/admin/"
echo "2. Vérifiez les fichiers statiques: http://votre-domaine.com/static/admin/css/base.css"
echo "3. Vérifiez les médias: http://votre-domaine.com/media/products/"
echo ""
echo "🔧 EN CAS DE PROBLÈME:"
echo "1. Vérifiez les logs Nginx: sudo journalctl -u nginx"
echo "2. Vérifiez les logs Gunicorn: sudo journalctl -u gunicorn"
echo "3. Vérifiez les permissions: ls -la $STATIC_DIR"
echo "4. Re-exécutez ce script si nécessaire"
echo ""
echo "✅ Vos fichiers statiques sont maintenant accessibles!"

