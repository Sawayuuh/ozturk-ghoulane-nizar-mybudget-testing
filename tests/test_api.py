"""
Tests d'intégration pour l'API
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date
from app.main import app
from app.database import Base, engine, get_db
from app.models import Transaction, Budget


# Créer une base de données de test
@pytest.fixture(scope="function")
def client():
    """Crée un client de test pour l'API"""
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


class TestTransactionsAPI:
    """Tests pour les endpoints de transactions"""
    
    def test_create_transaction(self, client):
        """Test de création d'une transaction"""
        response = client.post(
            "/api/transactions",
            json={
                "montant": 25.50,
                "libelle": "Courses Leclerc",
                "type": "depense",
                "categorie": "alimentation",
                "date_transaction": "2026-01-06"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["montant"] == 25.50
        assert data["libelle"] == "Courses Leclerc"
        assert data["type"] == "depense"
        assert data["categorie"] == "alimentation"
        assert "id" in data
    
    def test_create_transaction_invalide_montant_negatif(self, client):
        """Test de rejet d'une transaction avec montant négatif"""
        response = client.post(
            "/api/transactions",
            json={
                "montant": -10.0,
                "libelle": "Test",
                "type": "depense",
                "categorie": "alimentation",
                "date_transaction": "2026-01-06"
            }
        )
        assert response.status_code == 422
    
    def test_create_transaction_invalide_type(self, client):
        """Test de rejet d'une transaction avec type invalide"""
        response = client.post(
            "/api/transactions",
            json={
                "montant": 25.50,
                "libelle": "Test",
                "type": "invalid",
                "categorie": "alimentation",
                "date_transaction": "2026-01-06"
            }
        )
        assert response.status_code == 422
    
    def test_list_transactions(self, client):
        """Test de liste des transactions"""
        # Créer quelques transactions
        client.post("/api/transactions", json={
            "montant": 25.50,
            "libelle": "Courses",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-06"
        })
        client.post("/api/transactions", json={
            "montant": 800.0,
            "libelle": "Loyer",
            "type": "depense",
            "categorie": "logement",
            "date_transaction": "2026-01-01"
        })
        
        response = client.get("/api/transactions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_list_transactions_filtre_categorie(self, client):
        """Test de filtrage par catégorie"""
        client.post("/api/transactions", json={
            "montant": 25.50,
            "libelle": "Courses",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-06"
        })
        client.post("/api/transactions", json={
            "montant": 800.0,
            "libelle": "Loyer",
            "type": "depense",
            "categorie": "logement",
            "date_transaction": "2026-01-01"
        })
        
        response = client.get("/api/transactions?categorie=alimentation")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["categorie"] == "alimentation"
    
    def test_list_transactions_filtre_periode(self, client):
        """Test de filtrage par période"""
        client.post("/api/transactions", json={
            "montant": 25.50,
            "libelle": "Courses",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-06"
        })
        client.post("/api/transactions", json={
            "montant": 50.0,
            "libelle": "Restaurant",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-02-10"
        })
        
        response = client.get("/api/transactions?date_debut=2026-01-01&date_fin=2026-01-31")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["date_transaction"] == "2026-01-06"
    
    def test_get_transaction_by_id(self, client):
        """Test de récupération d'une transaction par ID"""
        create_response = client.post("/api/transactions", json={
            "montant": 25.50,
            "libelle": "Courses",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-06"
        })
        transaction_id = create_response.json()["id"]
        
        response = client.get(f"/api/transactions/{transaction_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction_id
    
    def test_get_transaction_not_found(self, client):
        """Test de récupération d'une transaction inexistante"""
        response = client.get("/api/transactions/999")
        assert response.status_code == 404
    
    def test_delete_transaction(self, client):
        """Test de suppression d'une transaction"""
        create_response = client.post("/api/transactions", json={
            "montant": 25.50,
            "libelle": "Courses",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-06"
        })
        transaction_id = create_response.json()["id"]
        
        response = client.delete(f"/api/transactions/{transaction_id}")
        assert response.status_code == 204
        
        # Vérifier que la transaction n'existe plus
        get_response = client.get(f"/api/transactions/{transaction_id}")
        assert get_response.status_code == 404


class TestBudgetsAPI:
    """Tests pour les endpoints de budgets"""
    
    def test_create_budget(self, client):
        """Test de création d'un budget"""
        response = client.post(
            "/api/budgets",
            json={
                "categorie": "alimentation",
                "montant_budget": 300.0,
                "mois": 1,
                "annee": 2026
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["categorie"] == "alimentation"
        assert data["montant_budget"] == 300.0
        assert data["mois"] == 1
        assert data["annee"] == 2026
        assert "id" in data
    
    def test_create_budget_duplicate(self, client):
        """Test de rejet d'un budget en double"""
        client.post("/api/budgets", json={
            "categorie": "alimentation",
            "montant_budget": 300.0,
            "mois": 1,
            "annee": 2026
        })
        
        response = client.post("/api/budgets", json={
            "categorie": "alimentation",
            "montant_budget": 400.0,
            "mois": 1,
            "annee": 2026
        })
        assert response.status_code == 400
    
    def test_create_budget_invalide_montant(self, client):
        """Test de rejet d'un budget avec montant invalide"""
        response = client.post("/api/budgets", json={
            "categorie": "alimentation",
            "montant_budget": -100.0,
            "mois": 1,
            "annee": 2026
        })
        assert response.status_code == 422
    
    def test_create_budget_invalide_mois(self, client):
        """Test de rejet d'un budget avec mois invalide"""
        response = client.post("/api/budgets", json={
            "categorie": "alimentation",
            "montant_budget": 300.0,
            "mois": 13,
            "annee": 2026
        })
        assert response.status_code == 422
    
    def test_list_budgets(self, client):
        """Test de liste des budgets"""
        client.post("/api/budgets", json={
            "categorie": "alimentation",
            "montant_budget": 300.0,
            "mois": 1,
            "annee": 2026
        })
        client.post("/api/budgets", json={
            "categorie": "logement",
            "montant_budget": 800.0,
            "mois": 1,
            "annee": 2026
        })
        
        response = client.get("/api/budgets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_budget_stats(self, client):
        """Test de récupération des statistiques d'un budget"""
        # Créer un budget
        client.post("/api/budgets", json={
            "categorie": "alimentation",
            "montant_budget": 300.0,
            "mois": 1,
            "annee": 2026
        })
        
        # Créer des dépenses
        client.post("/api/transactions", json={
            "montant": 25.50,
            "libelle": "Courses",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-06"
        })
        client.post("/api/transactions", json={
            "montant": 50.0,
            "libelle": "Restaurant",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-15"
        })
        
        response = client.get("/api/budgets/stats/alimentation?mois=1&annee=2026")
        assert response.status_code == 200
        data = response.json()
        assert data["categorie"] == "alimentation"
        assert data["periode"] == "01/2026"
        assert data["montant_total_depense"] == 75.50
        assert data["budget_fixe"] == 300.0
        assert data["montant_restant"] == 224.50
        assert abs(data["pourcentage_consomme"] - 25.17) < 0.1
    
    def test_list_all_budget_stats(self, client):
        """Test de liste de toutes les statistiques de budgets"""
        client.post("/api/budgets", json={
            "categorie": "alimentation",
            "montant_budget": 300.0,
            "mois": 1,
            "annee": 2026
        })
        client.post("/api/budgets", json={
            "categorie": "logement",
            "montant_budget": 800.0,
            "mois": 1,
            "annee": 2026
        })
        
        response = client.get("/api/budgets/stats?mois=1&annee=2026")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_create_transaction_alerte_depassement(self, client):
        """Alerte lorsque une dépense fait dépasser le budget"""
        client.post("/api/budgets", json={
            "categorie": "alimentation",
            "montant_budget": 300.0,
            "mois": 1,
            "annee": 2026
        })
        client.post("/api/transactions", json={
            "montant": 290.0,
            "libelle": "Courses",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-10"
        })
        response = client.post("/api/transactions", json={
            "montant": 20.0,
            "libelle": "Snack",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-15"
        })
        assert response.status_code == 201
        data = response.json()
        assert data.get("alerte_depassement") is True
        assert "Dépassement" in (data.get("message_alerte") or "")

    def test_export_transactions_csv(self, client):
        """Export des transactions en CSV"""
        client.post("/api/transactions", json={
            "montant": 25.50,
            "libelle": "Courses",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-06"
        })
        response = client.get("/api/transactions/export/csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "id,date,libelle,type,categorie,montant" in response.text
        assert "Courses" in response.text

    def test_update_transaction(self, client):
        """Modification d'une transaction"""
        create_resp = client.post("/api/transactions", json={
            "montant": 25.50,
            "libelle": "Courses",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-06"
        })
        tid = create_resp.json()["id"]
        response = client.put(f"/api/transactions/{tid}", json={
            "montant": 30.0,
            "libelle": "Courses modifié",
            "type": "depense",
            "categorie": "alimentation",
            "date_transaction": "2026-01-06"
        })
        assert response.status_code == 200
        assert response.json()["montant"] == 30.0
        assert response.json()["libelle"] == "Courses modifié"

    def test_get_budget_by_id(self, client):
        """Récupération d'un budget par ID"""
        create_resp = client.post("/api/budgets", json={
            "categorie": "alimentation",
            "montant_budget": 300.0,
            "mois": 1,
            "annee": 2026
        })
        bid = create_resp.json()["id"]
        response = client.get(f"/api/budgets/{bid}")
        assert response.status_code == 200
        assert response.json()["categorie"] == "alimentation"

    def test_update_budget(self, client):
        """Modification d'un budget"""
        create_resp = client.post("/api/budgets", json={
            "categorie": "alimentation",
            "montant_budget": 300.0,
            "mois": 1,
            "annee": 2026
        })
        bid = create_resp.json()["id"]
        response = client.put(f"/api/budgets/{bid}", json={
            "montant_budget": 350.0
        })
        assert response.status_code == 200
        assert response.json()["montant_budget"] == 350.0

    def test_delete_budget(self, client):
        """Suppression d'un budget"""
        create_resp = client.post("/api/budgets", json={
            "categorie": "alimentation",
            "montant_budget": 300.0,
            "mois": 1,
            "annee": 2026
        })
        bid = create_resp.json()["id"]
        response = client.delete(f"/api/budgets/{bid}")
        assert response.status_code == 204
        assert client.get(f"/api/budgets/{bid}").status_code == 404
