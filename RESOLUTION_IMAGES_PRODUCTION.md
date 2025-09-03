# 🖼️ RÉSOLUTION RAPIDE - Images des produits non visibles

## 📋 **PROBLÈME IDENTIFIÉ**

**Symptôme :** Les images des produits uploadées via l'admin ne s'affichent pas sur le site
**Cause :** Configuration des fichiers media non optimale en production

## 🚀 **SOLUTION IMMÉDIATE (10 minutes)**

### **1. Exécuter le diagnostic sur votre serveur :**
```bash
cd /var/www/ecom_maillot
python test_images_production.py
```

### **2. Appliquer la configuration Nginx :**
```bash
# Copier la nouvelle configuration
sudo cp nginx_images.conf /etc/nginx/sites-available/ecom_maillot

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
```

### **3. Redémarrer Django :**
```bash
# Si systemd
sudo systemctl restart ecom_maillot

# Ou gunicorn
pkill gunicorn
gunicorn --bind 127.0.0.1:8000 ecom_maillot.wsgi:application &
```

## 🔧 **CONFIGURATION CORRIGÉE**

### **wsgi.py - WhiteNoise pour les images :**
```python
# Configuration WhiteNoise pour servir les fichiers statiques ET media en production
from whitenoise import WhiteNoise
application = WhiteNoise(application, root='staticfiles/')

# Ajouter le dossier media pour servir les images des produits
media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
application.add_files(media_root, prefix='media/')
```

### **Nginx - Configuration des images :**
```nginx
# Configuration des fichiers media (IMAGES DES PRODUITS)
location /media/ {
    alias /var/www/ecom_maillot/media/;
    expires 1y;
    add_header Cache-Control "public, immutable";
    
    # Types MIME pour les images
    location ~* \.(jpg|jpeg|png|gif|webp)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
    }
}
```

## 🖼️ **TEST DES IMAGES**

### **1. Vérifier l'upload :**
- Connectez-vous à `/admin/`
- Créez un produit avec une image
- L'image doit être dans `/media/products/`

### **2. Tester l'accès direct :**
```bash
# Tester une image spécifique
curl -I http://orapide.shop/media/products/nom_image.jpg

# Vérifier les logs Nginx
sudo tail -f /var/log/nginx/error.log
```

### **3. Vérifier les permissions :**
```bash
# Donner les bonnes permissions
sudo chown -R www-data:www-data /var/www/ecom_maillot/media
sudo chmod -R 755 /var/www/ecom_maillot/media
```

## 🚨 **PROBLÈMES COURANTS ET SOLUTIONS**

### **Images toujours non visibles :**
```bash
# Vérifier que les images existent
ls -la /var/www/ecom_maillot/media/products/

# Vérifier les permissions
ls -la /var/www/ecom_maillot/media/

# Vérifier la configuration Nginx
sudo nginx -t
```

### **Erreur 404 sur les images :**
```bash
# Vérifier que Nginx sert bien /media/
curl -I http://orapide.shop/media/

# Vérifier les logs Nginx
sudo tail -f /var/log/nginx/access.log
```

### **Erreur 500 sur les images :**
```bash
# Vérifier les logs Django
tail -f /var/www/ecom_maillot/logs/django.log

# Vérifier la configuration
python manage.py check --deploy
```

## 📋 **CHECKLIST DE RÉSOLUTION**

- [ ] Diagnostic exécuté avec `test_images_production.py`
- [ ] Configuration Nginx mise à jour
- [ ] Nginx redémarré
- [ ] Django redémarré
- [ ] Permissions media vérifiées (755)
- [ ] Image testée via URL directe
- [ ] Images visibles sur le site

## 🎯 **RÉSULTAT ATTENDU**

Après la correction :
- ✅ Images uploadées via Admin visibles sur le site
- ✅ URLs des images : `http://orapide.shop/media/products/nom_image.jpg`
- ✅ Performance optimisée avec cache et compression
- ✅ Plus de placeholders gris

## 🔍 **VÉRIFICATIONS FINALES**

### **1. Test d'une image :**
```bash
# Créer une image de test
echo "test" > /var/www/ecom_maillot/media/test.txt

# Tester l'accès
curl http://orapide.shop/media/test.txt
```

### **2. Vérifier la structure :**
```
/var/www/ecom_maillot/
├── media/
│   ├── products/          # Images des produits
│   ├── teams/             # Logos des équipes
│   └── categories/        # Images des catégories
├── staticfiles/           # Fichiers statiques
└── manage.py
```

### **3. Vérifier les services :**
```bash
# Statut des services
sudo systemctl status nginx
sudo systemctl status ecom_maillot

# Logs en temps réel
sudo tail -f /var/log/nginx/error.log
```

## 🆘 **SUPPORT URGENT**

Si le problème persiste :

1. **Vérifiez les logs** : `sudo tail -f /var/log/nginx/error.log`
2. **Testez une image** : `curl http://orapide.shop/media/products/nom_image.jpg`
3. **Vérifiez les permissions** : `ls -la /var/www/ecom_maillot/media/`

**Vos images de maillots seront parfaitement visibles !** 🏆
