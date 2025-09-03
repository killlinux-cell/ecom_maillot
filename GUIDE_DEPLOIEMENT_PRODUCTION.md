# 🚀 Guide de Déploiement en Production - ecom_maillot

## 📋 **RÉPONSE À VOTRE QUESTION**

**OUI, vos images seront accessibles en ligne !** Voici pourquoi et comment :

### ✅ **Configuration actuelle CORRECTE :**
- WhiteNoise est installé et configuré
- `MEDIA_ROOT` et `STATIC_ROOT` sont définis
- Les modèles utilisent `upload_to` pour organiser les images
- Configuration WhiteNoise dans `wsgi.py` pour servir les fichiers media

### 🖼️ **Comment vos images seront servies :**
1. **Upload via Admin** → Stockage dans `/media/products/`, `/media/teams/`, etc.
2. **WhiteNoise** → Sert automatiquement les fichiers depuis `/media/`
3. **URLs** → `https://votre-domaine.com/media/products/image.jpg`

## 🛠️ **ÉTAPES DE DÉPLOIEMENT**

### 1. **Préparation du projet**
```bash
# Exécuter le script de déploiement
python deploy_production.py

# Ou manuellement :
python manage.py collectstatic --noinput
python manage.py check --deploy
```

### 2. **Configuration des variables d'environnement**
```bash
# Copier le fichier d'exemple
cp env.production.example .env

# Modifier .env avec vos vraies valeurs
nano .env
```

### 3. **Configuration de la base de données**
```bash
# Créer la base PostgreSQL
sudo -u postgres createdb ecom_maillot
sudo -u postgres createuser ecom_user

# Appliquer les migrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. **Configuration Nginx**
```bash
# Copier la configuration
sudo cp nginx.conf /etc/nginx/sites-available/ecom_maillot

# Activer le site
sudo ln -s /etc/nginx/sites-available/ecom_maillot /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
```

### 5. **Démarrage de l'application**
```bash
# Démarrer avec Gunicorn
gunicorn --bind 127.0.0.1:8000 ecom_maillot.wsgi:application

# Ou en arrière-plan
nohup gunicorn --bind 127.0.0.1:8000 ecom_maillot.wsgi:application &
```

## 🔧 **CONFIGURATION SYSTEMD (Recommandé)**

Créer `/etc/systemd/system/ecom_maillot.service` :

```ini
[Unit]
Description=Ecom Maillot Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/chemin/vers/votre/projet
Environment="PATH=/chemin/vers/votre/projet/venv/bin"
ExecStart=/chemin/vers/votre/projet/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 ecom_maillot.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

Puis :
```bash
sudo systemctl daemon-reload
sudo systemctl enable ecom_maillot
sudo systemctl start ecom_maillot
```

## 📁 **STRUCTURE DES DOSSIERS EN PRODUCTION**

```
/chemin/vers/votre/projet/
├── media/                    # Vos images uploadées
│   ├── products/            # Images des produits
│   ├── teams/               # Logos des équipes
│   └── categories/          # Images des catégories
├── staticfiles/             # Fichiers statiques collectés
├── logs/                    # Logs de l'application
├── .env                     # Variables d'environnement
└── manage.py
```

## 🖼️ **TEST DES IMAGES**

### 1. **Upload d'une image via Admin**
- Connectez-vous à `/admin/`
- Créez un produit avec une image
- L'image sera stockée dans `/media/products/`

### 2. **Vérification de l'URL**
- L'image sera accessible à : `https://votre-domaine.com/media/products/nom_image.jpg`
- Vérifiez dans votre navigateur

### 3. **Vérification des permissions**
```bash
# Donner les bonnes permissions
sudo chown -R www-data:www-data /chemin/vers/votre/projet/media
sudo chmod -R 755 /chemin/vers/votre/projet/media
```

## 🚨 **PROBLÈMES COURANTS ET SOLUTIONS**

### **Images non accessibles :**
```bash
# Vérifier les permissions
sudo chown -R www-data:www-data media/

# Vérifier la configuration Nginx
sudo nginx -t

# Vérifier les logs
sudo tail -f /var/log/nginx/error.log
```

### **Erreur 500 :**
```bash
# Vérifier les logs de l'application
tail -f logs/django.log

# Vérifier la configuration
python manage.py check --deploy
```

### **Fichiers statiques non trouvés :**
```bash
# Recollecter les fichiers statiques
python manage.py collectstatic --noinput --clear

# Vérifier STATIC_ROOT dans settings
echo $STATIC_ROOT
```

## 🔒 **SÉCURITÉ**

### **HTTPS (Recommandé) :**
```bash
# Installer Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d votre-domaine.com
```

### **Firewall :**
```bash
# Ouvrir seulement les ports nécessaires
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## 📊 **MONITORING**

### **Logs à surveiller :**
- `/var/log/nginx/access.log` - Accès au site
- `/var/log/nginx/error.log` - Erreurs Nginx
- `logs/django.log` - Logs de l'application

### **Commandes utiles :**
```bash
# Statut des services
sudo systemctl status nginx
sudo systemctl status ecom_maillot

# Espace disque
df -h

# Utilisation mémoire
free -h
```

## 🎯 **RÉSUMÉ**

**Vos images seront parfaitement accessibles en ligne car :**

1. ✅ **WhiteNoise** est configuré pour servir les fichiers media
2. ✅ **Nginx** est configuré pour servir les images avec cache
3. ✅ **Les modèles** utilisent `upload_to` pour organiser les fichiers
4. ✅ **Les URLs** sont correctement configurées

**Après déploiement :**
- Upload d'image via Admin → Stockage dans `/media/`
- Accès public → `https://votre-domaine.com/media/chemin/image.jpg`
- Performance optimisée avec cache et compression

**Votre boutique de maillots sera entièrement fonctionnelle avec toutes les images accessibles !** 🏆
