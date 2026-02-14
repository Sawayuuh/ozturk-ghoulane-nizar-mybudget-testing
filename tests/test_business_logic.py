"""
Tests unitaires pour la logique métier
"""
import pytest
from datetime import date
from app import business_logic
from app.models import Transaction, Budget


class TestCalculTotalDepenseParCategorie:
    """Tests pour calculer_total_depense_par_categorie"""
    
    def test_calcul_total_depense_categorie_simple(self, db_session, sample_transactions):
        """Test du calcul du total dépensé pour une catégorie"""
        total = business_logic.calculer_total_depense_par_categorie(
            db_session, "alimentation", 1, 2026
        )
        # 25.50 + 50.0 = 75.50
        assert total == 75.50
    
    def test_calcul_total_depense_categorie_inexistante(self, db_session):
        """Test avec une catégorie qui n'existe pas"""
        total = business_logic.calculer_total_depense_par_categorie(
            db_session, "inexistante", 1, 2026
        )
        assert total == 0.0
    
    def test_calcul_total_depense_mois_different(self, db_session, sample_transactions):
        """Test que les transactions d'un autre mois ne sont pas comptées"""
        total = business_logic.calculer_total_depense_par_categorie(
            db_session, "alimentation", 2, 2026
        )
        assert total == 0.0
    
    def test_calcul_total_depense_exclut_revenus(self, db_session, sample_transactions):
        """Test que les revenus ne sont pas comptés dans les dépenses"""
        total = business_logic.calculer_total_depense_par_categorie(
            db_session, "salaire", 1, 2026
        )
        assert total == 0.0


class TestCalculMontantRestantBudget:
    """Tests pour calculer_montant_restant_budget"""
    
    def test_calcul_montant_restant_budget_normal(self, db_session, sample_transactions, sample_budgets):
        """Test du calcul du montant restant sur un budget"""
        montant_restant = business_logic.calculer_montant_restant_budget(
            db_session, "alimentation", 1, 2026
        )
        # Budget: 300€, Dépenses: 75.50€, Restant: 224.50€
        assert montant_restant == 224.50
    
    def test_calcul_montant_restant_budget_depasse(self, db_session, sample_budgets):
        """Test avec un budget dépassé"""
        # Ajouter une dépense importante
        transaction = Transaction(
            montant=500.0,
            libelle="Gros achat",
            type="depense",
            categorie="alimentation",
            date_transaction=date(2026, 1, 10)
        )
        db_session.add(transaction)
        db_session.commit()
        
        montant_restant = business_logic.calculer_montant_restant_budget(
            db_session, "alimentation", 1, 2026
        )
        # Budget: 300€, Dépenses: 500€, Restant: -200€ (dépassement)
        assert montant_restant == -200.0
    
    def test_calcul_montant_restant_budget_inexistant(self, db_session):
        """Test avec un budget qui n'existe pas"""
        montant_restant = business_logic.calculer_montant_restant_budget(
            db_session, "inexistante", 1, 2026
        )
        assert montant_restant == 0.0


class TestCalculPourcentageConsomme:
    """Tests pour calculer_pourcentage_consomme"""
    
    def test_calcul_pourcentage_consomme_normal(self, db_session, sample_transactions, sample_budgets):
        """Test du calcul du pourcentage consommé"""
        pourcentage = business_logic.calculer_pourcentage_consomme(
            db_session, "alimentation", 1, 2026
        )
        # Budget: 300€, Dépenses: 75.50€, Pourcentage: 25.17%
        assert abs(pourcentage - 25.17) < 0.1
    
    def test_calcul_pourcentage_consomme_depasse(self, db_session, sample_budgets):
        """Test avec un budget dépassé (plus de 100%)"""
        transaction = Transaction(
            montant=400.0,
            libelle="Gros achat",
            type="depense",
            categorie="alimentation",
            date_transaction=date(2026, 1, 10)
        )
        db_session.add(transaction)
        db_session.commit()
        
        pourcentage = business_logic.calculer_pourcentage_consomme(
            db_session, "alimentation", 1, 2026
        )
        # Budget: 300€, Dépenses: 400€, Pourcentage: 133.33%
        assert abs(pourcentage - 133.33) < 0.1
    
    def test_calcul_pourcentage_budget_inexistant(self, db_session):
        """Test avec un budget qui n'existe pas"""
        pourcentage = business_logic.calculer_pourcentage_consomme(
            db_session, "inexistante", 1, 2026
        )
        assert pourcentage == 0.0


class TestObtenirStatistiquesBudget:
    """Tests pour obtenir_statistiques_budget"""
    
    def test_obtenir_statistiques_budget_complet(self, db_session, sample_transactions, sample_budgets):
        """Test de l'obtention complète des statistiques"""
        stats = business_logic.obtenir_statistiques_budget(
            db_session, "alimentation", 1, 2026
        )
        
        assert stats["categorie"] == "alimentation"
        assert stats["periode"] == "01/2026"
        assert stats["montant_total_depense"] == 75.50
        assert stats["budget_fixe"] == 300.0
        assert stats["montant_restant"] == 224.50
        assert abs(stats["pourcentage_consomme"] - 25.17) < 0.1
    
    def test_obtenir_statistiques_budget_inexistant(self, db_session):
        """Test avec un budget qui n'existe pas"""
        stats = business_logic.obtenir_statistiques_budget(
            db_session, "inexistante", 1, 2026
        )
        
        assert stats["categorie"] == "inexistante"
        assert stats["montant_total_depense"] == 0.0
        assert stats["budget_fixe"] == 0.0
        assert stats["montant_restant"] == 0.0
        assert stats["pourcentage_consomme"] == 0.0


class TestVerifierDepassementBudget:
    """Tests pour verifier_depassement_budget (alerte dépassement)"""
    
    def test_pas_de_depassement(self, db_session, sample_transactions, sample_budgets):
        """Ajout d'une dépense qui reste sous le budget"""
        alerte = business_logic.verifier_depassement_budget(
            db_session, "alimentation", 1, 2026, 50.0
        )
        assert alerte["depasse"] is False
        assert alerte["message_alerte"] is None
        assert alerte["montant_restant_avant"] == 224.50
    
    def test_depassement_budget(self, db_session, sample_transactions, sample_budgets):
        """Ajout d'une dépense qui fait dépasser le budget (290 + 20 > 300)"""
        alerte = business_logic.verifier_depassement_budget(
            db_session, "alimentation", 1, 2026, 250.0
        )
        assert alerte["depasse"] is True
        assert "Dépassement" in (alerte["message_alerte"] or "")
        assert alerte["budget_fixe"] == 300.0
    
    def test_categorie_sans_budget(self, db_session, sample_transactions):
        """Catégorie sans budget défini -> pas d'alerte"""
        alerte = business_logic.verifier_depassement_budget(
            db_session, "loisirs", 1, 2026, 100.0
        )
        assert alerte["depasse"] is False
        assert alerte["message_alerte"] is None
