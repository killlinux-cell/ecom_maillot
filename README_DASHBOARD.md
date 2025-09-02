# Guide d'Utilisation du Dashboard E-commerce Maillots

## 🎯 Vue d'ensemble

Ce dashboard personnalisé remplace l'interface d'administration Django par défaut et centralise toutes les fonctionnalités de gestion de votre boutique de maillots de football.

## 🚀 Accès au Dashboard

### URL d'accès
```
http://votre-domaine.com/dashboard/
```

### Authentification
- Seuls les utilisateurs avec le statut "staff" peuvent accéder au dashboard
- Utilisez vos identifiants Django existants

## 📊 Sections du Dashboard

### 1. Tableau de Bord Principal (`/dashboard/`)
- **Statistiques générales** : Commandes, revenus, clients, produits
- **Graphiques** : Évolution des ventes, répartition des commandes
- **Dernières commandes** : Vue rapide des commandes récentes
- **Produits populaires** : Articles les plus vendus
- **Actions rapides** : Accès direct aux fonctions principales
- **Notifications** : Alertes et informations importantes

### 2. Gestion des Produits (`/dashboard/products/`)
- **Liste des produits** avec recherche et filtres
- **Ajout/Modification** de produits
- **Gestion des images** et descriptions
- **Contrôle des stocks** et prix
- **Statuts** (actif/inactif, en vedette)

### 3. Gestion des Catégories (`/dashboard/categories/`)
- **Création** de nouvelles catégories
- **Modification** des catégories existantes
- **Organisation** de votre catalogue

### 4. Gestion des Équipes (`/dashboard/teams/`)
- **Ajout** de nouvelles équipes de football
- **Gestion** des logos et informations
- **Organisation** par ligue ou pays

### 5. Gestion des Utilisateurs (`/dashboard/users/`)
- **Liste des clients** avec recherche
- **Modification** des profils utilisateurs
- **Contrôle des statuts** (actif/inactif, staff)
- **Gestion des permissions**

### 6. Gestion des Commandes (`/dashboard/orders/`)
- **Suivi** de toutes les commandes
- **Filtres** par statut et date
- **Modification** des statuts
- **Détails** complets des commandes
- **Gestion** des livraisons

### 7. Gestion des Paiements (`/dashboard/payments/`)
- **Suivi** des transactions
- **Filtres** par méthode et statut
- **Graphiques** d'évolution des paiements
- **Gestion** des statuts de paiement

### 8. Gestion des Personnalisations (`/dashboard/customizations/`)
- **Suivi** des demandes de personnalisation
- **Filtres** par produit
- **Validation** des personnalisations
- **Gestion** des statuts

### 9. Analyses et Rapports (`/dashboard/analytics/`)
- **Ventes mensuelles** avec graphiques
- **Produits** les plus performants
- **Performance** des équipes
- **Statistiques** détaillées

### 10. Paramètres (`/dashboard/settings/`)
- **Configuration** générale du site
- **Paramètres** des passerelles de paiement
- **Options** de livraison
- **Configuration** des emails

## 🛠️ Fonctionnalités Avancées

### Recherche et Filtres
- **Recherche textuelle** dans tous les modules
- **Filtres par date** et statut
- **Pagination** automatique des résultats
- **Tri** par différents critères

### Actions en Lot
- **Sélection multiple** d'éléments
- **Modification** en masse des statuts
- **Suppression** groupée (avec confirmation)

### Export de Données
- **Export CSV** des listes
- **Rapports PDF** des analyses
- **Sauvegarde** des données

### Notifications
- **Alertes** de stock faible
- **Notifications** de nouvelles commandes
- **Rappels** de tâches à effectuer

## 📱 Interface Responsive

Le dashboard s'adapte automatiquement à tous les écrans :
- **Desktop** : Interface complète avec sidebar
- **Tablette** : Navigation adaptée
- **Mobile** : Menu hamburger et layout optimisé

## 🎨 Personnalisation

### Thèmes
- **Mode clair/sombre** (à venir)
- **Couleurs personnalisables**
- **Logos** de votre entreprise

### Widgets
- **Réorganisation** des sections
- **Ajout/suppression** de widgets
- **Personnalisation** des graphiques

## 🔒 Sécurité

### Authentification
- **Session sécurisée** avec timeout
- **Vérification** des permissions
- **Logs** d'accès et actions

### Permissions
- **Niveaux d'accès** différents
- **Restriction** par fonctionnalité
- **Audit trail** des modifications

## 📈 Performance

### Optimisations
- **Cache** des requêtes fréquentes
- **Lazy loading** des images
- **Pagination** des résultats
- **Compression** des assets

### Monitoring
- **Temps de réponse** des pages
- **Utilisation** des ressources
- **Alertes** de performance

## 🚨 Dépannage

### Problèmes Courants

#### Dashboard ne se charge pas
1. Vérifiez que l'utilisateur a le statut "staff"
2. Contrôlez les permissions dans Django admin
3. Vérifiez les logs d'erreur

#### Graphiques ne s'affichent pas
1. Assurez-vous que Chart.js est chargé
2. Vérifiez la console JavaScript
3. Contrôlez les données passées aux templates

#### Recherche ne fonctionne pas
1. Vérifiez la configuration des filtres
2. Contrôlez les paramètres GET
3. Testez avec des termes simples

### Logs et Debug
- **Console Django** : `python manage.py runserver`
- **Console navigateur** : F12 → Console
- **Logs serveur** : `/var/log/` (Linux) ou Event Viewer (Windows)

## 🔄 Mise à Jour

### Procédure de Mise à Jour
1. **Sauvegarde** de la base de données
2. **Pull** des dernières modifications
3. **Migration** de la base de données
4. **Collecte** des fichiers statiques
5. **Redémarrage** du serveur

### Vérifications Post-Mise à Jour
- **Fonctionnalités** principales
- **Permissions** utilisateurs
- **Données** et configurations
- **Performance** générale

## 📞 Support

### Documentation
- **Ce guide** d'utilisation
- **Commentaires** dans le code
- **Docstrings** des fonctions

### Contact
- **Développeur** : [Votre nom/email]
- **Documentation** : [Lien vers la doc]
- **Issues** : [Lien vers le système de tickets]

## 🎉 Conclusion

Ce dashboard offre une interface moderne et intuitive pour gérer votre boutique de maillots. Il centralise toutes les fonctionnalités nécessaires et remplace efficacement l'interface Django admin par défaut.

**Bonne utilisation !** 🚀
