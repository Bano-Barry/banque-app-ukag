# 🏦 Système de Gestion Bancaire - Django

Application web de gestion bancaire développée avec Django pour le projet de Génie Logiciel - Master 1 IASD, Université Kofi Annan de Guinée.

---

## 📋 Table des matières

- [Description](#description)
- [Fonctionnalités](#fonctionnalités)
- [Technologies utilisées](#technologies-utilisées)
- [Installation](#installation)
- [Structure du projet](#structure-du-projet)
- [Utilisation](#utilisation)
- [Modèles de données](#modèles-de-données)
- [Auteurs](#auteurs)

---

## 📖 Description

Cette application permet de gérer un système bancaire complet avec :

- Gestion des agences bancaires
- Gestion des clients
- Gestion de trois types de comptes (Épargne, Courant, Payant)
- Opérations bancaires (dépôts, retraits, virements)
- Historique complet des opérations

Le projet respecte les principes de la Programmation Orientée Objet (POO) et les bonnes pratiques du développement web Django.

---

## ✨ Fonctionnalités

### Gestion des entités

- ✅ Création et gestion des agences
- ✅ Création et gestion des clients
- ✅ Création de comptes bancaires (3 types)

### Types de comptes

1. **Compte Épargne**
   - Taux d'intérêt de 5%
   - Méthode de calcul automatique des intérêts

2. **Compte Courant**
   - Découvert autorisé
   - Possibilité de solde négatif (dans la limite du découvert)

3. **Compte Payant**
   - Frais de 15 GNF par opération (dépôt et retrait)

### Opérations bancaires

- 💰 Dépôt d'argent
- 💸 Retrait d'argent
- 🔄 Virement entre comptes
- 📊 Consultation du solde
- 📜 Historique complet des opérations
- 📈 Calcul des intérêts (Comptes Épargne)

---

## 🛠️ Technologies utilisées

- **Backend** : Python 3.12.3
- **Framework** : Django 5.x
- **Base de données** : SQLite (développement) / PostgreSQL (production recommandée)
- **Frontend** : HTML5, CSS3, Bootstrap 5
- **Versioning** : Git

---

## 🚀 Installation

### Prérequis

- Python 3.12.3 ou supérieur
- pip (gestionnaire de paquets Python)
- Virtualenv (recommandé)

### Étapes d'installation

1. **Cloner le projet**

```bash
git clone <url-du-repo>
cd BanqueApp
```

2. **Créer un environnement virtuel**

```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

4. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

5. **Effectuer les migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Créer un superutilisateur (admin)**

```bash
python manage.py createsuperuser
```

7. **Lancer le serveur de développement**

```bash
python manage.py runserver
```

8. **Accéder à l'application**

- Interface principale : http://127.0.0.1:8000/
- Interface admin : http://127.0.0.1:8000/admin/

---

## 📁 Structure du projet

```
BanqueApp/
├── banque_project/          # Configuration du projet Django
│   ├── __init__.py
│   ├── settings.py         # Paramètres du projet
│   ├── urls.py             # URLs principales
│   └── wsgi.py
├── banque/                  # Application principale
│   ├── migrations/         # Migrations de base de données
│   ├── templates/          # Templates HTML
│   ├── static/             # Fichiers statiques (CSS, JS, images)
│   ├── __init__.py
│   ├── admin.py            # Configuration de l'interface admin
│   ├── models.py           # Modèles de données
│   ├── views.py            # Vues (logique métier)
│   ├── urls.py             # URLs de l'application
│   └── forms.py            # Formulaires Django
├── venv/                    # Environnement virtuel (non versionné)
├── db.sqlite3              # Base de données SQLite (non versionné)
├── manage.py               # Script de gestion Django
├── requirements.txt        # Dépendances Python
└── README.md               # Ce fichier
```

---

## 📊 Modèles de données

### Diagramme des relations

```
Agence (1) ----< (N) Client (1) ----< (1) Compte (1) ----< (N) Operation
                                              |
                                              +-- CompteEpargne
                                              +-- CompteCourant
                                              +-- ComptePayant
```

### Détails des modèles

#### **Agence**

- `code` : Code unique de l'agence
- `nom` : Nom de l'agence
- `adresse` : Adresse complète

#### **Client**

- `numero` : Numéro unique du client
- `nom` : Nom de famille
- `prenom` : Prénom
- `sexe` : Sexe (M/F)
- `telephone` : Numéro de téléphone
- `agence` : Agence de rattachement (ForeignKey)

#### **Compte**

- `code` : Code auto-incrémenté
- `solde` : Solde actuel
- `type_compte` : Type (EPARGNE, COURANT, PAYANT)
- `date_creation` : Date de création automatique
- `client` : Client propriétaire (OneToOneField)

#### **CompteEpargne** (détails)

- `compte` : Référence au compte (OneToOneField)
- `taux_interet` : Taux d'intérêt (défaut : 5%)

#### **CompteCourant** (détails)

- `compte` : Référence au compte (OneToOneField)
- `decouvert` : Découvert autorisé

#### **ComptePayant** (détails)

- `compte` : Référence au compte (OneToOneField)
- `FRAIS_OPERATION` : Constante de 15 GNF

#### **Operation**

- `compte` : Compte concerné (ForeignKey)
- `type_operation` : Type (DEPOT, RETRAIT, VIREMENT, etc.)
- `montant` : Montant de l'opération
- `solde_apres` : Solde après l'opération
- `date` : Date et heure automatiques

---

## 🎯 Utilisation

### Interface Admin

1. Se connecter à `/admin/` avec les identifiants superutilisateur
2. Gérer les agences, clients, comptes et consulter les opérations

### Interface utilisateur (à venir)

L'interface web grand public permettra :

- Consultation des comptes
- Effectuer des opérations bancaires
- Visualiser l'historique
- Générer des rapports

---

## 🧪 Tests

Pour exécuter les tests :

```bash
python manage.py test banque
```

---

## 📝 Règles de gestion

1. Une agence gère plusieurs clients
2. Un client possède UN SEUL compte bancaire
3. Un compte peut être de type Épargne, Courant ou Payant
4. Les codes de compte sont auto-incrémentés
5. Le solde d'un compte est en lecture seule (modifié uniquement via opérations)
6. Toutes les opérations sont tracées dans l'historique
7. Les Comptes Payants ont des frais de 15 GNF par dépôt/retrait
8. Les Comptes Courants acceptent un solde négatif (jusqu'au découvert)
9. Les Comptes Épargne génèrent des intérêts de 5%

---

## 👥 Auteurs

**Projet académique - Master 1 IASD**

- Université Kofi Annan de Guinée (UKAG)
- Faculté des Sciences Informatiques
- Cours : Génie Logiciel
- Année universitaire : 2024-2025

---

## 📄 Licence

Projet académique - Usage éducatif uniquement

---

## 🔄 Changelog

### Version 1.0.0 (Février 2025)

- ✅ Modèles de données complets
- ✅ Migrations de base de données
- ✅ Interface admin configurée
- 🚧 Interface utilisateur (en développement)

---

## 📞 Support

Pour toute question ou problème :

- Créer une issue sur le repository
- Contacter l'équipe de développement

---

**Fait avec ❤️ à Conakry, Guinée 🇬🇳**
