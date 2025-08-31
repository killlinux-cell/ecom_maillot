# Guide d'utilisation - Paiement Wave Direct

## Vue d'ensemble

Le système de paiement Wave Direct a été modifié pour permettre aux utilisateurs de soumettre l'ID de transaction après avoir effectué le paiement manuel. Cela permet à l'administrateur de vérifier et valider les paiements.

## Processus pour l'utilisateur

### 1. Sélection du mode de paiement
- L'utilisateur choisit "Wave Direct" lors du paiement
- Il est redirigé vers la page de paiement Wave

### 2. Instructions de paiement
La page affiche :
- Le numéro Wave à payer
- Le montant exact
- Le code de paiement unique
- Les instructions détaillées

### 3. Effectuer le paiement
L'utilisateur doit :
1. Ouvrir l'application Wave
2. Aller dans "Envoyer de l'argent"
3. Entrer le numéro Wave affiché
4. Entrer le montant exact
5. Dans la description, écrire le code de paiement
6. Confirmer le paiement

### 4. Soumettre l'ID de transaction
Après le paiement :
1. L'utilisateur reçoit un SMS avec l'ID de transaction
2. Il clique sur "J'ai effectué le paiement"
3. Il saisit l'ID de transaction dans le formulaire
4. Il saisit son numéro de téléphone
5. Il soumet le formulaire

### 5. Attente de validation
- Le paiement passe en statut "En attente de validation"
- L'utilisateur reçoit une confirmation
- Il peut suivre le statut sur la page de détail de commande

## Processus pour l'administrateur

### 1. Accès aux paiements
- Aller dans l'interface d'administration Django
- Section "Paiements"
- Filtrer par méthode "Wave Direct"

### 2. Vérification des paiements
L'admin peut voir :
- L'ID de transaction soumis
- Le numéro de téléphone du client
- Le montant et les détails de la commande
- Le statut actuel

### 3. Validation des paiements
L'admin peut :
- Vérifier l'ID de transaction avec Wave
- Valider le paiement en cliquant sur "Valider les paiements Wave sélectionnés"
- Marquer comme échoué si nécessaire

### 4. Actions disponibles
- **Valider les paiements Wave sélectionnés** : Valide les paiements en attente
- **Marquer comme terminé** : Marque manuellement comme payé
- **Marquer comme échoué** : Marque comme échoué

## Fonctionnalités techniques

### Champs ajoutés/modifiés
- `wave_transaction_id` : Stocke l'ID de transaction soumis
- `customer_phone` : Numéro de téléphone du client
- `status` : Statut du paiement (pending/completed/failed)

### Logs automatiques
Le système crée automatiquement des logs pour :
- Soumission de l'ID de transaction
- Validation par l'admin
- Changements de statut

### Validation des données
- L'ID de transaction doit contenir uniquement des lettres et chiffres
- Le numéro de téléphone est requis
- Validation côté client et serveur

## URLs importantes

- **Paiement Wave** : `/payments/wave/<order_id>/`
- **Soumission transaction** : `/payments/wave/submit-transaction/<order_id>/`
- **Admin paiements** : `/admin/payments/payment/`

## Messages utilisateur

### Succès
- "Votre ID de transaction a été soumis avec succès !"
- "Notre équipe va vérifier le paiement et valider votre commande"

### Erreurs
- "L'ID de transaction est requis"
- "L'ID de transaction contient des caractères invalides"
- "Le numéro de téléphone est requis"

## Sécurité

- Validation CSRF sur tous les formulaires
- Vérification des permissions utilisateur
- Logs détaillés pour audit
- Validation des données côté serveur

## Support

En cas de problème :
1. Vérifier les logs dans l'admin
2. Contacter le support technique
3. Consulter la documentation Wave
