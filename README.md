# E-commerce Maillots de Football

Site e-commerce moderne dédié à la vente de maillots de football avec intégration Wave Côte d'Ivoire via PayDunya.

## Fonctionnalités

- 🏠 Page d'accueil avec produits phares et promotions
- 🛍️ Catalogue de produits avec filtres avancés
- 📱 Interface responsive et moderne
- 🛒 Panier d'achat dynamique
- 💳 Paiement sécurisé via Wave (PayDunya)
- 👤 Espace utilisateur complet
- ⚙️ Back-office administrateur

## Installation

### Prérequis
- Python 3.8+
- pip
- virtualenv (recommandé)

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd ecom_maillot
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

5. **Appliquer les migrations**
```bash
python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

## Configuration PayDunya

1. Créer un compte sur [PayDunya](https://paydunya.com)
2. Configurer les clés API dans le fichier `.env`
3. Tester les paiements en mode sandbox

## Structure du projet

```
ecom_maillot/
├── ecom_maillot/          # Configuration principale Django
├── accounts/              # Gestion des utilisateurs
├── products/              # Gestion des produits
├── cart/                  # Panier d'achat
├── orders/                # Gestion des commandes
├── payments/              # Intégration PayDunya
├── static/                # Fichiers statiques
├── templates/             # Templates HTML
└── media/                 # Images uploadées
```

## Déploiement

Le projet est configuré pour être déployé sur Heroku, Railway ou tout autre service cloud.

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.
