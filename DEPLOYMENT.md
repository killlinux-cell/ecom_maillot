# Guide de Déploiement - E-commerce Maillots de Football

Ce guide vous accompagne dans le déploiement de votre site e-commerce Django sur différentes plateformes.

## 🚀 Déploiement sur Heroku

### Prérequis
- Compte Heroku
- Git installé
- Heroku CLI installé

### Étapes de déploiement

1. **Créer une application Heroku**
```bash
heroku create votre-app-name
```

2. **Configurer les variables d'environnement**
```bash
heroku config:set SECRET_KEY="votre-secret-key-securisee"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="votre-app-name.herokuapp.com"
heroku config:set PAYDUNYA_MODE=live
heroku config:set PAYDUNYA_MASTER_KEY="votre-master-key"
heroku config:set PAYDUNYA_PUBLIC_KEY="votre-public-key"
heroku config:set PAYDUNYA_PRIVATE_KEY="votre-private-key"
heroku config:set PAYDUNYA_TOKEN="votre-token"
```

3. **Configurer la base de données PostgreSQL**
```bash
heroku addons:create heroku-postgresql:mini
```

4. **Déployer l'application**
```bash
git add .
git commit -m "Initial deployment"
git push heroku main
```

5. **Appliquer les migrations**
```bash
heroku run python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
heroku run python manage.py createsuperuser
```

7. **Collecter les fichiers statiques**
```bash
heroku run python manage.py collectstatic --noinput
```

## 🌐 Déploiement sur Railway

### Prérequis
- Compte Railway
- Git installé

### Étapes de déploiement

1. **Connecter votre repository GitHub à Railway**

2. **Configurer les variables d'environnement dans Railway Dashboard**

3. **Déployer automatiquement**

## 📧 Configuration Email

### Gmail SMTP
```bash
heroku config:set EMAIL_HOST=smtp.gmail.com
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER=votre-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=votre-app-password
```

### SendGrid (Recommandé pour la production)
```bash
heroku addons:create sendgrid:starter
```

## 🔐 Configuration PayDunya

### Mode Test
```bash
heroku config:set PAYDUNYA_MODE=test
```

### Mode Production
```bash
heroku config:set PAYDUNYA_MODE=live
```

### Obtenir les clés PayDunya
1. Créer un compte sur [PayDunya](https://paydunya.com)
2. Accéder à votre dashboard
3. Récupérer les clés API dans la section développeur

## 📱 Configuration du domaine personnalisé

### Heroku
```bash
heroku domains:add www.votre-domaine.com
heroku domains:add votre-domaine.com
```

### Configuration DNS
- Ajouter un enregistrement CNAME pointant vers votre-app-name.herokuapp.com
- Ajouter un enregistrement A pour la racine du domaine

## 🔒 Sécurité

### Variables d'environnement critiques
- `SECRET_KEY` : Clé secrète Django
- `PAYDUNYA_*` : Clés PayDunya
- `EMAIL_*` : Configuration email
- `DATABASE_URL` : URL de la base de données

### Recommandations
- Utiliser HTTPS en production
- Configurer les en-têtes de sécurité
- Activer la protection CSRF
- Limiter les tentatives de connexion

## 📊 Monitoring

### Heroku
```bash
heroku logs --tail
heroku ps
```

### Métriques recommandées
- Temps de réponse
- Taux d'erreur
- Utilisation de la base de données
- Trafic utilisateur

## 🔄 Mises à jour

### Déploiement continu
```bash
git add .
git commit -m "Description des changements"
git push heroku main
```

### Rollback en cas de problème
```bash
heroku rollback
```

## 🛠️ Maintenance

### Sauvegarde de la base de données
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

### Mise à jour des dépendances
```bash
pip install --upgrade -r requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push heroku main
```

## 📞 Support

En cas de problème :
1. Vérifier les logs : `heroku logs --tail`
2. Tester localement : `python manage.py runserver`
3. Vérifier la configuration des variables d'environnement
4. Consulter la documentation Django et Heroku

## 🎯 Checklist de déploiement

- [ ] Variables d'environnement configurées
- [ ] Base de données configurée
- [ ] Migrations appliquées
- [ ] Superutilisateur créé
- [ ] Fichiers statiques collectés
- [ ] PayDunya configuré
- [ ] Email configuré
- [ ] HTTPS activé
- [ ] Tests effectués
- [ ] Monitoring configuré
