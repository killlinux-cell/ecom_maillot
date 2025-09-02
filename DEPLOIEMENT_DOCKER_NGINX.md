# Guide de Déploiement Django avec Docker et Nginx sur VPS

## 📋 Prérequis
- VPS Ubuntu 20.04+ ou Debian 11+
- Accès SSH root
- Domaine configuré (ex: `orapide.shop`)
- Git installé sur votre machine locale

---

## 🐳 Étape 1: Préparation du Projet (Machine Locale)

### 1.1 Créer les fichiers Docker

#### `Dockerfile`
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gcc \
        g++ \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements.txt
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer l'utilisateur non-root
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Exposer le port
EXPOSE 8000

# Commande par défaut
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "ecom_maillot.wsgi:application"]
```

#### `docker-compose.yml`
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=ecom_maillot
      - POSTGRES_USER=ecom_user
      - POSTGRES_PASSWORD=your_secure_password_here
    restart: unless-stopped
    networks:
      - ecom_network

  web:
    build: .
    restart: unless-stopped
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./logs:/app/logs
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://ecom_user:your_secure_password_here@db:5432/ecom_maillot
      - SECRET_KEY=your_django_secret_key_here
      - ALLOWED_HOSTS=orapide.shop,www.orapide.shop,localhost,127.0.0.1
      - SITE_URL=https://orapide.shop
    depends_on:
      - db
    networks:
      - ecom_network

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/sites-available:/etc/nginx/sites-available
      - ./nginx/sites-enabled:/etc/nginx/sites-enabled
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - web
    networks:
      - ecom_network

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  ecom_network:
    driver: bridge
```

#### `requirements.txt` (mise à jour)
```txt
Django==4.2.7
psycopg2-binary==2.9.7
gunicorn==21.2.0
python-decouple==3.8
crispy-forms==2.0
crispy-bootstrap5==0.7
django-allauth==0.57.0
django-filter==23.3
django-cors-headers==4.3.1
whitenoise==6.6.0
Pillow==10.1.0
django-imagekit==5.0.0
```

### 1.2 Configuration Nginx

#### `nginx/nginx.conf`
```nginx
# nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Include site configurations
    include /etc/nginx/sites-enabled/*;
}
```

#### `nginx/sites-available/ecom_maillot`
```nginx
# nginx/sites-available/ecom_maillot
upstream django {
    server web:8000;
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name orapide.shop www.orapide.shop;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name orapide.shop www.orapide.shop;

    # SSL configuration
    ssl_certificate /etc/nginx/ssl/orapide.shop.crt;
    ssl_certificate_key /etc/nginx/ssl/orapide.shop.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Media files
    location /media/ {
        alias /app/media/;
        expires 1y;
        add_header Cache-Control "public";
        access_log off;
    }

    # Django admin
    location /admin/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Login pages
    location ~ ^/(accounts/login|accounts/signup) {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Main application
    location / {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 1.3 Configuration Django pour Production

#### `ecom_maillot/settings_production.py`
```python
# ecom_maillot/settings_production.py
from .settings import *
import os
from decouple import config

# Security
DEBUG = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='ecom_maillot'),
        'USER': config('POSTGRES_USER', default='ecom_user'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='your_secure_password_here'),
        'HOST': config('POSTGRES_HOST', default='db'),
        'PORT': config('POSTGRES_PORT', default='5432'),
    }
}

# Static files
STATIC_ROOT = '/app/staticfiles'
MEDIA_ROOT = '/app/media'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email (à configurer selon votre fournisseur)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Allowed hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='orapide.shop,www.orapide.shop,localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Site URL
SITE_URL = config('SITE_URL', default='https://orapide.shop')
```

---

## 🚀 Étape 2: Configuration du VPS

### 2.1 Connexion et mise à jour
```bash
# Se connecter au VPS
ssh root@your_vps_ip

# Mettre à jour le système
apt update && apt upgrade -y

# Installer les packages nécessaires
apt install -y curl wget git ufw fail2ban
```

### 2.2 Installation de Docker
```bash
# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Installer Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Démarrer Docker
systemctl start docker
systemctl enable docker

# Vérifier l'installation
docker --version
docker-compose --version
```

### 2.3 Configuration de la sécurité
```bash
# Configurer UFW
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw enable

# Configurer Fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### 2.4 Créer l'utilisateur pour l'application
```bash
# Créer l'utilisateur
adduser ecom
usermod -aG docker ecom

# Créer le répertoire de l'application
mkdir -p /home/ecom/ecom_maillot
chown ecom:ecom /home/ecom/ecom_maillot
```

---

## 📦 Étape 3: Déploiement de l'Application

### 3.1 Cloner le projet
```bash
# Se connecter en tant qu'utilisateur ecom
su - ecom

# Cloner le projet
cd /home/ecom
git clone https://github.com/votre-username/ecom_maillot.git
cd ecom_maillot
```

### 3.2 Créer les fichiers de configuration
```bash
# Créer les répertoires nécessaires
mkdir -p nginx/sites-available nginx/sites-enabled logs ssl

# Copier les fichiers de configuration
# (Vous devrez créer ces fichiers avec le contenu fourni ci-dessus)
```

### 3.3 Configuration SSL (Let's Encrypt)
```bash
# Installer Certbot
sudo apt install certbot

# Obtenir le certificat SSL
sudo certbot certonly --standalone -d orapide.shop -d www.orapide.shop

# Copier les certificats
sudo cp /etc/letsencrypt/live/orapide.shop/fullchain.pem /home/ecom/ecom_maillot/ssl/orapide.shop.crt
sudo cp /etc/letsencrypt/live/orapide.shop/privkey.pem /home/ecom/ecom_maillot/ssl/orapide.shop.key
sudo chown ecom:ecom /home/ecom/ecom_maillot/ssl/*
```

### 3.4 Variables d'environnement
```bash
# Créer le fichier .env
cat > .env << EOF
DEBUG=False
SECRET_KEY=your_super_secret_key_here
DATABASE_URL=postgresql://ecom_user:your_secure_password_here@db:5432/ecom_maillot
POSTGRES_DB=ecom_maillot
POSTGRES_USER=ecom_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_HOST=db
POSTGRES_PORT=5432
ALLOWED_HOSTS=orapide.shop,www.orapide.shop,localhost,127.0.0.1
SITE_URL=https://orapide.shop
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
PAYDUNYA_MASTER_KEY=your_paydunya_master_key
PAYDUNYA_PUBLIC_KEY=your_paydunya_public_key
PAYDUNYA_PRIVATE_KEY=your_paydunya_private_key
PAYDUNYA_TOKEN=your_paydunya_token
PAYDUNYA_MODE=live
WAVE_PHONE_NUMBER=+2250575984322
WAVE_PAYMENT_ENABLED=True
WAVE_MERCHANT_ID=your_wave_merchant_id
WAVE_API_KEY=your_wave_api_key
WAVE_SECRET_KEY=your_wave_secret_key
EOF
```

### 3.5 Construire et démarrer les conteneurs
```bash
# Construire les images
docker-compose build

# Démarrer les services
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

### 3.6 Configuration de la base de données
```bash
# Créer les migrations
docker-compose exec web python manage.py makemigrations

# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Collecter les fichiers statiques
docker-compose exec web python manage.py collectstatic --noinput

# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser
```

---

## 🔧 Étape 4: Configuration DNS

### 4.1 Pointer le domaine vers le VPS
Dans votre gestionnaire de DNS, créez ces enregistrements :

```
Type: A
Nom: @
Valeur: VOTRE_IP_VPS

Type: A
Nom: www
Valeur: VOTRE_IP_VPS
```

### 4.2 Vérifier la propagation DNS
```bash
# Vérifier la propagation
nslookup orapide.shop
dig orapide.shop
```

---

## 🛠️ Étape 5: Maintenance et Monitoring

### 5.1 Script de déploiement automatique
```bash
# deploy.sh
#!/bin/bash
cd /home/ecom/ecom_maillot

# Pull les dernières modifications
git pull origin main

# Reconstruire et redémarrer
docker-compose down
docker-compose build
docker-compose up -d

# Appliquer les migrations
docker-compose exec -T web python manage.py migrate

# Collecter les fichiers statiques
docker-compose exec -T web python manage.py collectstatic --noinput

# Redémarrer Nginx
docker-compose restart nginx

echo "Déploiement terminé!"
```

### 5.2 Monitoring des logs
```bash
# Voir les logs en temps réel
docker-compose logs -f

# Logs spécifiques
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db
```

### 5.3 Sauvegarde automatique
```bash
# backup.sh
#!/bin/bash
BACKUP_DIR="/home/ecom/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Créer le répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarder la base de données
docker-compose exec -T db pg_dump -U ecom_user ecom_maillot > $BACKUP_DIR/db_backup_$DATE.sql

# Sauvegarder les fichiers media
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz media/

# Supprimer les sauvegardes de plus de 7 jours
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Sauvegarde terminée: $DATE"
```

### 5.4 Renouvellement SSL automatique
```bash
# Ajouter au crontab
crontab -e

# Ajouter cette ligne
0 12 * * * certbot renew --quiet && docker-compose restart nginx
```

---

## 🔍 Étape 6: Tests et Vérification

### 6.1 Tests de base
```bash
# Vérifier que tous les services fonctionnent
docker-compose ps

# Tester l'application
curl -I https://orapide.shop

# Vérifier les logs
docker-compose logs web
```

### 6.2 Tests de performance
```bash
# Installer Apache Bench
apt install apache2-utils

# Test de charge
ab -n 1000 -c 10 https://orapide.shop/
```

---

## 🚨 Dépannage

### Problèmes courants

#### 1. Erreur 502 Bad Gateway
```bash
# Vérifier les logs
docker-compose logs nginx
docker-compose logs web

# Vérifier la connectivité
docker-compose exec nginx ping web
```

#### 2. Problèmes de base de données
```bash
# Vérifier la connexion
docker-compose exec web python manage.py dbshell

# Redémarrer la base de données
docker-compose restart db
```

#### 3. Problèmes SSL
```bash
# Vérifier les certificats
openssl x509 -in ssl/orapide.shop.crt -text -noout

# Renouveler les certificats
certbot renew
```

---

## 📊 Monitoring et Optimisation

### 1. Monitoring des ressources
```bash
# Installer htop
apt install htop

# Surveiller les ressources
htop
docker stats
```

### 2. Optimisation Nginx
```bash
# Ajuster le nombre de workers
# Dans nginx.conf, modifier worker_processes selon le nombre de CPU
worker_processes auto;
```

### 3. Optimisation Django
```python
# Dans settings_production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}
```

---

## 🎯 Conclusion

Votre application Django est maintenant déployée avec Docker et Nginx ! 

**Points clés :**
- ✅ Application conteneurisée avec Docker
- ✅ Base de données PostgreSQL
- ✅ Serveur web Nginx avec SSL
- ✅ Sécurité configurée (UFW, Fail2ban)
- ✅ Monitoring et sauvegarde automatiques
- ✅ Déploiement automatisé

**Prochaines étapes :**
1. Configurer les emails SMTP
2. Mettre en place un CDN pour les fichiers statiques
3. Configurer un monitoring plus avancé (Prometheus/Grafana)
4. Mettre en place des tests automatisés

Votre site est accessible sur `https://orapide.shop` ! 🚀
