# 🐳 Déploiement Docker - Ecom Maillot

Guide complet pour déployer votre application Django avec Docker et Nginx sur un VPS.

## 📋 Prérequis

- VPS Ubuntu 20.04+ ou Debian 11+
- Accès SSH root
- Domaine configuré (ex: `orapide.shop`)
- Git installé sur votre machine locale

## 🚀 Déploiement Rapide

### 1. Configuration du VPS

```bash
# Se connecter au VPS
ssh root@your_vps_ip

# Exécuter le script de configuration
wget https://raw.githubusercontent.com/votre-username/ecom_maillot/main/setup_vps.sh
chmod +x setup_vps.sh
./setup_vps.sh
```

### 2. Déploiement de l'Application

```bash
# Se connecter en tant qu'utilisateur ecom
su - ecom

# Cloner le projet
cd /home/ecom
git clone https://github.com/votre-username/ecom_maillot.git
cd ecom_maillot

# Configurer les variables d'environnement
cp env.example .env
nano .env  # Modifier les valeurs

# Obtenir les certificats SSL
sudo certbot certonly --standalone -d orapide.shop -d www.orapide.shop

# Copier les certificats
sudo cp /etc/letsencrypt/live/orapide.shop/fullchain.pem ssl/orapide.shop.crt
sudo cp /etc/letsencrypt/live/orapide.shop/privkey.pem ssl/orapide.shop.key
sudo chown ecom:ecom ssl/*

# Démarrer l'application
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

## 📁 Structure des Fichiers

```
ecom_maillot/
├── Dockerfile                 # Configuration Docker pour Django
├── docker-compose.yml         # Orchestration des services
├── .dockerignore             # Fichiers exclus du contexte Docker
├── env.example               # Variables d'environnement d'exemple
├── deploy.sh                 # Script de déploiement automatique
├── backup.sh                 # Script de sauvegarde
├── setup_vps.sh              # Configuration initiale du VPS
├── nginx/
│   ├── nginx.conf            # Configuration principale Nginx
│   ├── sites-available/
│   │   └── ecom_maillot      # Configuration du site
│   └── sites-enabled/
│       └── ecom_maillot      # Lien vers sites-available
├── logs/                     # Logs de l'application
└── ssl/                      # Certificats SSL
```

## 🔧 Services Docker

### 1. Base de Données (PostgreSQL)
- **Image**: `postgres:15`
- **Port**: 5432 (interne)
- **Volume**: `postgres_data`
- **Variables**: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

### 2. Application Django
- **Image**: Construite localement
- **Port**: 8000 (interne)
- **Volumes**: `static_volume`, `media_volume`, `logs`
- **Dépendances**: Base de données

### 3. Serveur Web (Nginx)
- **Image**: `nginx:alpine`
- **Ports**: 80, 443 (externes)
- **Volumes**: Configuration Nginx, fichiers statiques/media, SSL
- **Dépendances**: Application Django

## 🔒 Sécurité

### Firewall (UFW)
```bash
# Vérifier le statut
ufw status

# Ajouter des règles si nécessaire
ufw allow from your_ip_address
```

### Fail2ban
```bash
# Vérifier le statut
fail2ban-client status

# Voir les IPs bannies
fail2ban-client status sshd
```

### Certificats SSL
```bash
# Renouveler automatiquement
crontab -e
# Ajouter: 0 12 * * * certbot renew --quiet && docker-compose restart nginx
```

## 📊 Monitoring

### Logs
```bash
# Logs en temps réel
docker-compose logs -f

# Logs spécifiques
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db
```

### Ressources
```bash
# Utilisation des conteneurs
docker stats

# Utilisation du système
htop
```

### Santé des Services
```bash
# Vérifier le statut
docker-compose ps

# Test de santé
curl -f http://localhost/health/
```

## 🔄 Maintenance

### Déploiement Automatique
```bash
# Exécuter le script de déploiement
./deploy.sh
```

### Sauvegarde Automatique
```bash
# Exécuter la sauvegarde
./backup.sh

# Configurer la sauvegarde automatique
crontab -e
# Ajouter: 0 2 * * * /home/ecom/ecom_maillot/backup.sh
```

### Mise à Jour
```bash
# Mettre à jour l'application
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

## 🚨 Dépannage

### Erreur 502 Bad Gateway
```bash
# Vérifier les logs
docker-compose logs nginx
docker-compose logs web

# Vérifier la connectivité
docker-compose exec nginx ping web
```

### Problèmes de Base de Données
```bash
# Vérifier la connexion
docker-compose exec web python manage.py dbshell

# Redémarrer la base de données
docker-compose restart db
```

### Problèmes SSL
```bash
# Vérifier les certificats
openssl x509 -in ssl/orapide.shop.crt -text -noout

# Renouveler les certificats
certbot renew
```

## 📈 Optimisation

### Performance Nginx
```nginx
# Dans nginx.conf
worker_processes auto;  # Selon le nombre de CPU
worker_connections 1024;
```

### Performance Django
```python
# Dans settings_production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}
```

### Performance PostgreSQL
```bash
# Dans docker-compose.yml
db:
  environment:
    - POSTGRES_SHARED_PRELOAD_LIBRARIES=pg_stat_statements
```

## 🎯 Commandes Utiles

```bash
# Redémarrer tous les services
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart web

# Voir les logs d'un service
docker-compose logs web

# Accéder au shell d'un conteneur
docker-compose exec web bash

# Exécuter une commande Django
docker-compose exec web python manage.py shell

# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser

# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Collecter les fichiers statiques
docker-compose exec web python manage.py collectstatic --noinput
```

## 📞 Support

En cas de problème :
1. Vérifiez les logs : `docker-compose logs`
2. Consultez le guide de dépannage
3. Vérifiez la documentation Docker
4. Contactez le support technique

---

**Votre application est maintenant déployée avec Docker ! 🚀**
