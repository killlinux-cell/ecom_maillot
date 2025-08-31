# Guide d'Optimisation - VPS 1GB RAM

## 🎯 Configuration cible
- **CPU :** 1 vCore
- **RAM :** 1 Go
- **Stockage :** 10 Go NVMe SSD
- **Datacenter :** UE

## ✅ Optimisations système

### 1. Configuration PostgreSQL
```bash
# /etc/postgresql/14/main/postgresql.conf
shared_buffers = 128MB          # 25% de la RAM
effective_cache_size = 256MB    # 50% de la RAM
work_mem = 2MB                  # Réduit pour économiser la RAM
maintenance_work_mem = 32MB     # Réduit pour les opérations de maintenance
```

### 2. Configuration Gunicorn
```bash
# /etc/systemd/system/gunicorn.service
[Service]
ExecStart=/home/ecom_maillot/venv/bin/gunicorn \
    --workers 2 \
    --worker-class sync \
    --worker-connections 100 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --preload \
    ecom_maillot.wsgi:application
```

### 3. Configuration Nginx
```nginx
# /etc/nginx/nginx.conf
worker_processes 1;
worker_connections 512;
keepalive_timeout 65;
client_max_body_size 10M;  # Limite upload images

# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript;
```

## 📊 Allocation mémoire recommandée

| Service | RAM | % |
|---------|-----|---|
| **Système** | 200 MB | 20% |
| **PostgreSQL** | 300 MB | 30% |
| **Gunicorn** | 400 MB | 40% |
| **Nginx** | 50 MB | 5% |
| **Cache/Disponible** | 50 MB | 5% |

## 🔧 Optimisations Django

### 1. Settings de production
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['votre-domaine.com', 'www.votre-domaine.com']

# Cache en mémoire (Redis trop lourd pour 1GB)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Optimisation des requêtes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ecom_maillot',
        'USER': 'ecom_user',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 10,  # Limite connexions
        }
    }
}

# Compression des fichiers statiques
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

### 2. Optimisation des modèles
```python
# Utiliser select_related et prefetch_related
# Exemple dans views.py
products = Product.objects.select_related('category', 'team').prefetch_related('images')[:20]
```

### 3. Pagination
```python
# Limiter les résultats
from django.core.paginator import Paginator

def product_list(request):
    products = Product.objects.filter(is_active=True)
    paginator = Paginator(products, 12)  # 12 produits par page
    page = request.GET.get('page')
    products = paginator.get_page(page)
```

## 🖼️ Gestion des images

### 1. Compression automatique
```python
# requirements.txt
Pillow==10.0.0
django-imagekit==5.2.0

# models.py
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit

class ProductImage(models.Model):
    image = ProcessedImageField(
        upload_to='products/',
        processors=[ResizeToFit(800, 800)],
        format='JPEG',
        options={'quality': 85}
    )
```

### 2. Stockage externe (optionnel)
```python
# Pour économiser l'espace disque
import boto3
from storages.backends.s3boto3 import S3Boto3Storage

# AWS S3 ou DigitalOcean Spaces
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = 'votre_clé'
AWS_SECRET_ACCESS_KEY = 'votre_secret'
AWS_STORAGE_BUCKET_NAME = 'votre-bucket'
```

## 📈 Monitoring et surveillance

### 1. Script de monitoring
```bash
#!/bin/bash
# /home/ecom_maillot/monitor.sh

echo "=== Monitoring VPS 1GB ==="
echo "Date: $(date)"
echo "RAM: $(free -h | grep Mem)"
echo "Disque: $(df -h /)"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
echo "Processus:"
ps aux --sort=-%mem | head -10
```

### 2. Alerte automatique
```bash
# /etc/cron.d/monitor
*/5 * * * * root /home/ecom_maillot/monitor.sh >> /var/log/vps_monitor.log
```

## 🚀 Script de déploiement optimisé

```bash
#!/bin/bash
# deploy_1gb.sh

echo "🚀 Déploiement optimisé pour VPS 1GB"

# 1. Configuration système
echo "📋 Configuration système..."
sudo sysctl -w vm.swappiness=10
sudo sysctl -w vm.vfs_cache_pressure=50

# 2. PostgreSQL optimisé
echo "🗄️ Configuration PostgreSQL..."
sudo -u postgres psql -c "ALTER SYSTEM SET shared_buffers = '128MB';"
sudo -u postgres psql -c "ALTER SYSTEM SET effective_cache_size = '256MB';"
sudo -u postgres psql -c "ALTER SYSTEM SET work_mem = '2MB';"
sudo systemctl restart postgresql

# 3. Application
echo "🐍 Déploiement application..."
cd /home/ecom_maillot
source venv/bin/activate
python manage.py collectstatic --noinput
python manage.py migrate

# 4. Services
echo "⚙️ Configuration services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Déploiement terminé!"
```

## 📊 Capacité estimée

| Métrique | Capacité |
|----------|----------|
| **Utilisateurs simultanés** | 10-20 |
| **Requêtes/minute** | 100-200 |
| **Images stockées** | ~1000 (avec compression) |
| **Produits** | Illimité (base de données) |
| **Commandes/jour** | 50-100 |

## 🔄 Évolutivité

### Quand passer à 2GB RAM :
- Plus de 20 utilisateurs simultanés
- Plus de 200 requêtes/minute
- Besoin de cache Redis
- Plus d'images à stocker

### Migration simple :
```bash
# Sauvegarde
pg_dump ecom_maillot > backup.sql
tar -czf media_backup.tar.gz media/

# Restauration sur nouveau VPS
psql ecom_maillot < backup.sql
tar -xzf media_backup.tar.gz
```

## 💡 Conseils supplémentaires

1. **Backup quotidien** - Automatiser les sauvegardes
2. **Monitoring** - Surveiller l'utilisation des ressources
3. **Cache** - Utiliser le cache Django efficacement
4. **CDN** - Pour les images statiques (optionnel)
5. **Optimisation DB** - Index appropriés, requêtes optimisées

## 🎯 Conclusion

**Votre projet peut parfaitement fonctionner sur 1GB RAM** avec ces optimisations. C'est une excellente solution pour démarrer et tester votre e-commerce de maillots !
