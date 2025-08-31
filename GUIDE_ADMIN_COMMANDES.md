# Guide d'administration - Gestion des commandes

## Vue d'ensemble

Le système a été modifié pour permettre aux administrateurs d'accéder et de gérer toutes les commandes, pas seulement leurs propres commandes.

## Fonctionnalités d'administration

### ✅ **Accès aux commandes**

**Avant** : Les administrateurs ne pouvaient voir que leurs propres commandes
**Maintenant** : Les administrateurs peuvent voir et gérer toutes les commandes

### ✅ **Permissions d'administration**

Les utilisateurs avec les permissions suivantes ont accès complet :
- `is_staff = True` (Staff)
- `is_superuser = True` (Superuser)

### ✅ **Fonctionnalités disponibles**

1. **Voir toutes les commandes** : `/orders/`
2. **Voir le détail de n'importe quelle commande** : `/orders/detail/<id>/`
3. **Annuler n'importe quelle commande**
4. **Accéder aux paiements de toutes les commandes**
5. **Valider les paiements Wave**

## Interface utilisateur

### **Liste des commandes**
- **Titre** : "Toutes les Commandes" (au lieu de "Mes Commandes")
- **Badge** : "Vue Admin" affiché
- **Informations client** : Nom et email du client affichés pour chaque commande

### **Détail d'une commande**
- **Badge** : "Vue Admin" affiché
- **Section client** : Informations détaillées du client (nom, email, ID)
- **Actions** : Possibilité d'annuler la commande

### **Paiements**
- **Accès** : L'admin peut accéder aux pages de paiement de toutes les commandes
- **Validation** : L'admin peut valider les paiements Wave via l'interface d'administration

## URLs importantes

### **Commandes**
- **Liste** : `http://127.0.0.1:8000/orders/`
- **Détail** : `http://127.0.0.1:8000/orders/detail/<id>/`
- **Annulation** : `http://127.0.0.1:8000/orders/cancel/<id>/`

### **Paiements**
- **Wave Direct** : `http://127.0.0.1:8000/payments/wave/<id>/`
- **Soumission transaction** : `http://127.0.0.1:8000/payments/wave/submit-transaction/<id>/`

### **Administration**
- **Admin paiements** : `http://127.0.0.1:8000/admin/payments/payment/`

## Processus de gestion

### **1. Voir toutes les commandes**
1. Connectez-vous en tant qu'administrateur
2. Allez sur `/orders/`
3. Vous verrez toutes les commandes avec les informations des clients

### **2. Examiner une commande**
1. Cliquez sur une commande pour voir les détails
2. Vous verrez toutes les informations : client, articles, adresse, statut
3. Le badge "Vue Admin" confirme que vous êtes en mode administration

### **3. Gérer les paiements Wave**
1. Allez sur la page de paiement Wave de la commande
2. Vous pouvez voir les instructions et le code de paiement
3. L'utilisateur peut soumettre l'ID de transaction
4. Vous pouvez valider le paiement dans l'admin

### **4. Valider les paiements**
1. Allez dans l'interface d'administration Django
2. Section "Paiements"
3. Filtrez par méthode "Wave Direct"
4. Sélectionnez les paiements à valider
5. Cliquez sur "Valider les paiements Wave sélectionnés"

## Sécurité

### **Permissions**
- Seuls les utilisateurs avec `is_staff=True` ou `is_superuser=True` ont accès
- Les utilisateurs normaux ne peuvent toujours voir que leurs propres commandes

### **Logs**
- Toutes les actions d'administration sont loggées
- Les validations de paiement sont tracées

### **Validation**
- Les données sont validées côté serveur
- Les permissions sont vérifiées à chaque requête

## Messages d'interface

### **Indicateurs visuels**
- **Badge "Vue Admin"** : Confirme le mode administration
- **"Toutes les Commandes"** : Titre pour les administrateurs
- **Informations client** : Affichées pour les administrateurs

### **Actions disponibles**
- **Annuler commande** : Disponible pour toutes les commandes
- **Voir paiements** : Accès aux pages de paiement
- **Valider paiements** : Via l'interface d'administration

## Support

En cas de problème :
1. Vérifiez que l'utilisateur a les bonnes permissions (`is_staff=True`)
2. Vérifiez les logs dans l'administration
3. Testez avec un utilisateur superuser si nécessaire
