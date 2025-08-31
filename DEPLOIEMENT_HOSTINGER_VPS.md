# Guide de Déploiement - E-commerce Maillots sur Hostinger VPS

## 📋 Prérequis
- VPS Hostinger Ubuntu 20.04/22.04
- Nom de domaine configuré
- Accès SSH

## 🚀 Étape 1: Configuration initiale

### Connexion et mise à jour
```bash
ssh root@votre_ip_serveur
apt update && apt upgrade -y
```

### Installation des paquets
```bash
apt install -y python3 python3-pip python3-venv nginx git
apt install -y postgresql postgresql-contrib
apt install -y supervisor certbot python3-certbot-nginx
```

### Configuration du pare-feu
```bash
ufw allow 22,80,443
ufw enable
```

## 🗄️ Étape 2: PostgreSQL

### Configuration de la base de données
```bash
sudo -u postgres psql
CREATE DATABASE ecom_maillot;
CREATE USER ecom_user WITH PASSWORD 'mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE ecom_maillot TO ecom_user;
\q
```

## 👤 Étape 3: Utilisateur système

```bash
adduser ecom
usermod -aG sudo ecom
mkdir -p /home/ecom/.ssh
cp ~/.ssh/authorized_keys /home/ecom/.ssh/
chown -R ecom:ecom /home/ecom/.ssh
```

## 📁 Étape 4: Déploiement de l'app

### Connexion et clonage
```bash
su - ecom
cd /home/ecom
git clone https://github.com/votre_username/ecom_maillot.git
cd ecom_maillot
```

### Environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn psycopg2-binary
```

### Configuration
```bash
cp env.example .env
nano .env
```

Contenu `.env` :
```env
DEBUG=False
SECRET_KEY=votre_cle_secrete
ALLOWED_HOSTS=votre_domaine.com,www.votre_domaine.com
DATABASE_URL=postgresql://ecom_user:mot_de_passe@localhost/ecom_maillot
STATIC_ROOT=/home/ecom/ecom_maillot/staticfiles
MEDIA_ROOT=/home/ecom/ecom_maillot/media
```

### Migration et collecte statiques
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 🔧 Étape 5: Gunicorn

### Service Gunicorn
```bash
sudo nano /etc/systemd/system/gunicorn_ecom.service
```

Contenu :
```ini
[Unit]
Description=Gunicorn E-commerce Maillots
After=network.target

[Service]
User=ecom
Group=www-data
WorkingDirectory=/home/ecom/ecom_maillot
ExecStart=/home/ecom/ecom_maillot/venv/bin/gunicorn --workers 3 --bind unix:/home/ecom/ecom_maillot/ecom_maillot.sock ecom_maillot.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start gunicorn_ecom
sudo systemctl enable gunicorn_ecom
```

## 🌐 Étape 6: Nginx

### Configuration Nginx
```bash
sudo nano /etc/nginx/sites-available/ecom_maillot
```

Contenu :
```nginx
server {
    listen 80;
    server_name votre_domaine.com www.votre_domaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votre_domaine.com www.votre_domaine.com;

    ssl_certificate /etc/letsencrypt/live/votre_domaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre_domaine.com/privkey.pem;

    location /static/ {
        alias /home/ecom/ecom_maillot/staticfiles/;
    }

    location /media/ {
        alias /home/ecom/ecom_maillot/media/;
    }

    location / {
        proxy_pass http://unix:/home/ecom/ecom_maillot/ecom_maillot.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ecom_maillot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Étape 7: SSL

```bash
sudo certbot --nginx -d votre_domaine.com -d www.votre_domaine.com
sudo certbot renew --dry-run
```

## 🔄 Étape 8: Script de déploiement

```bash
nano /home/ecom/deploy.sh
```

Contenu :
```bash
#!/bin/bash
cd /home/ecom/ecom_maillot
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn_ecom
sudo systemctl restart nginx
echo "✅ Déploiement terminé!"
```

```bash
chmod +x /home/ecom/deploy.sh
```

## 📊 Étape 9: Sauvegardes

```bash
mkdir -p /home/ecom/backups
crontab -e
```

Ajoutez :
```bash
0 2 * * * pg_dump -U ecom_user ecom_maillot > /home/ecom/backups/backup_$(date +\%Y\%m\%d).sql
0 3 * * * find /home/ecom/backups -name "backup_*.sql" -mtime +7 -delete
```

## 🛡️ Étape 10: Sécurité

```bash
sudo apt install fail2ban
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## ✅ Test final

```bash
sudo systemctl status nginx gunicorn_ecom postgresql
curl -I https://votre_domaine.com
```

Votre site est accessible : `https://votre_domaine.com`

## 🔧 Dépannage

- **Erreur 502** : `sudo systemctl restart gunicorn_ecom`
- **Permissions** : `sudo chown -R ecom:www-data /home/ecom/ecom_maillot`
- **Base de données** : `sudo systemctl restart postgresql`
- **SSL** : `sudo certbot renew && sudo systemctl restart nginx`
