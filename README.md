# 💰 Gestion de Budget Personnel

Application web de gestion de budget personnel permettant d'enregistrer ses revenus et dépenses, de les organiser par catégories et de suivre des budgets mensuels.

## 🚀 Fonctionnalités

### MVP Implémenté

✅ **Saisie des transactions**
- Ajout de transactions (revenus ou dépenses) avec montant, libellé, type, catégorie et date
- Liste des transactions avec filtres par catégorie et période
- Suppression de transactions

✅ **Gestion des budgets par catégorie**
- Définition de budgets mensuels par catégorie
- Consultation des statistiques :
  - Montant total dépensé
  - Budget fixé
  - Montant restant (ou dépassement)
  - Pourcentage de budget consommé

✅ **Tests automatisés**
- Tests unitaires pour la logique métier (80%+ de couverture)
- Tests d'intégration pour l'API
- Validation des données et gestion des erreurs

## 📋 Prérequis

- Python 3.8+
- pip

## 🛠️ Installation

1. Cloner le projet :
```bash
git clone <url-du-repo>
cd ozturk-ghoulane-reverte-nizar-mybudget-testing
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## ▶️ Lancement

### Démarrer le serveur

```bash
uvicorn app.main:app --reload
```

L'application sera accessible à l'adresse : http://localhost:8000

### Interface web

Ouvrez votre navigateur et accédez à : http://localhost:8000

L'interface propose 3 onglets :
- **Transactions** : Ajouter et gérer vos transactions
- **Budgets** : Définir vos budgets mensuels par catégorie
- **Statistiques** : Consulter le suivi de vos budgets

## 🧪 Tests

### Lancer tous les tests

```bash
pytest
```

### Lancer les tests avec couverture

```bash
pytest --cov=app --cov-report=html
```

La couverture de code sera générée dans le dossier `htmlcov/`. Ouvrez `htmlcov/index.html` dans votre navigateur pour voir le rapport détaillé.

### Lancer uniquement les tests unitaires

```bash
pytest tests/test_business_logic.py
```

### Lancer uniquement les tests d'intégration

```bash
pytest tests/test_api.py
```

## 📁 Structure du projet

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # API FastAPI
│   ├── database.py          # Configuration SQLAlchemy
│   ├── models.py            # Modèles de données
│   ├── schemas.py           # Schémas Pydantic pour validation
│   └── business_logic.py   # Logique métier (calculs)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Configuration pytest
│   ├── test_business_logic.py  # Tests unitaires
│   └── test_api.py          # Tests d'intégration
├── static/
│   ├── index.html           # Interface web
│   ├── style.css            # Styles CSS
│   └── app.js               # JavaScript frontend
├── requirements.txt         # Dépendances Python
└── README.md               # Ce fichier
```

## 🔌 API Endpoints

### Transactions

- `POST /api/transactions` - Créer une transaction
- `GET /api/transactions` - Lister les transactions (filtres: `categorie`, `date_debut`, `date_fin`)
- `GET /api/transactions/{id}` - Récupérer une transaction
- `DELETE /api/transactions/{id}` - Supprimer une transaction

### Budgets

- `POST /api/budgets` - Créer un budget
- `GET /api/budgets` - Lister les budgets (filtres: `categorie`, `mois`, `annee`)
- `GET /api/budgets/stats/{categorie}` - Statistiques d'un budget (paramètres: `mois`, `annee`)
- `GET /api/budgets/stats` - Statistiques de tous les budgets (paramètres: `mois`, `annee`)

## 📊 Exemples d'utilisation

### Ajouter une transaction (CLI)

```bash
curl -X POST "http://localhost:8000/api/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "montant": 25.50,
    "libelle": "Courses Leclerc",
    "type": "depense",
    "categorie": "alimentation",
    "date_transaction": "2026-01-06"
  }'
```

### Créer un budget

```bash
curl -X POST "http://localhost:8000/api/budgets" \
  -H "Content-Type: application/json" \
  -d '{
    "categorie": "alimentation",
    "montant_budget": 300.0,
    "mois": 1,
    "annee": 2026
  }'
```

### Consulter les statistiques

```bash
curl "http://localhost:8000/api/budgets/stats/alimentation?mois=1&annee=2026"
```

## 🧩 Technologies utilisées

- **Backend** : FastAPI (Python)
- **Base de données** : SQLite avec SQLAlchemy ORM
- **Validation** : Pydantic
- **Tests** : pytest, pytest-cov
- **Frontend** : HTML5, CSS3, JavaScript (vanilla)

## 📝 Notes

- La base de données SQLite (`budget.db`) est créée automatiquement au premier lancement
- Les tests utilisent une base de données en mémoire pour l'isolation
- L'interface web est responsive et fonctionne sur mobile

## 👥 Auteurs

Projet réalisé dans le cadre du cours B3-2 EPSI.
