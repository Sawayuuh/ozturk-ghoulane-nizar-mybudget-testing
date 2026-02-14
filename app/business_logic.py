"""
Logique métier pour les calculs de budgets et transactions
"""
from sqlalchemy.orm import Session
from datetime import date
from app.models import Transaction, Budget


def calculer_total_depense_par_categorie(
    db: Session, 
    categorie: str, 
    mois: int,
    annee: int
) -> float:
    """
    Calcule le total des dépenses pour une catégorie sur un mois donné.
    
    Args:
        db: Session de base de données
        categorie: Nom de la catégorie
        mois: Mois (1-12)
        annee: Année
        
    Returns:
        Total des dépenses pour cette catégorie sur ce mois
    """
    # Calculer la date de début et de fin du mois
    date_debut = date(annee, mois, 1)
    if mois == 12:
        date_fin = date(annee + 1, 1, 1)
    else:
        date_fin = date(annee, mois + 1, 1)
    
    transactions = db.query(Transaction).filter(
        Transaction.categorie == categorie,
        Transaction.type == "depense",
        Transaction.date_transaction >= date_debut,
        Transaction.date_transaction < date_fin
    ).all()
    
    return sum(t.montant for t in transactions)


def calculer_montant_restant_budget(
    db: Session,
    categorie: str,
    mois: int,
    annee: int
) -> float:
    """
    Calcule le montant restant sur un budget.
    
    Args:
        db: Session de base de données
        categorie: Nom de la catégorie
        mois: Mois (1-12)
        annee: Année
        
    Returns:
        Montant restant (peut être négatif si dépassement)
    """
    budget = db.query(Budget).filter(
        Budget.categorie == categorie,
        Budget.mois == mois,
        Budget.annee == annee
    ).first()
    
    if not budget:
        return 0.0
    
    total_depense = calculer_total_depense_par_categorie(db, categorie, mois, annee)
    return budget.montant_budget - total_depense


def calculer_pourcentage_consomme(
    db: Session,
    categorie: str,
    mois: int,
    annee: int
) -> float:
    """
    Calcule le pourcentage de budget consommé.
    
    Args:
        db: Session de base de données
        categorie: Nom de la catégorie
        mois: Mois (1-12)
        annee: Année
        
    Returns:
        Pourcentage consommé (peut dépasser 100% en cas de dépassement)
    """
    budget = db.query(Budget).filter(
        Budget.categorie == categorie,
        Budget.mois == mois,
        Budget.annee == annee
    ).first()
    
    if not budget or budget.montant_budget == 0:
        return 0.0
    
    total_depense = calculer_total_depense_par_categorie(db, categorie, mois, annee)
    return (total_depense / budget.montant_budget) * 100


def obtenir_statistiques_budget(
    db: Session,
    categorie: str,
    mois: int,
    annee: int
) -> dict:
    """
    Obtient toutes les statistiques d'un budget pour une catégorie et une période.
    
    Args:
        db: Session de base de données
        categorie: Nom de la catégorie
        mois: Mois (1-12)
        annee: Année
        
    Returns:
        Dictionnaire avec toutes les statistiques
    """
    budget = db.query(Budget).filter(
        Budget.categorie == categorie,
        Budget.mois == mois,
        Budget.annee == annee
    ).first()
    
    if not budget:
        return {
            "categorie": categorie,
            "periode": f"{mois:02d}/{annee}",
            "montant_total_depense": 0.0,
            "budget_fixe": 0.0,
            "montant_restant": 0.0,
            "pourcentage_consomme": 0.0
        }
    
    total_depense = calculer_total_depense_par_categorie(db, categorie, mois, annee)
    montant_restant = budget.montant_budget - total_depense
    pourcentage = (total_depense / budget.montant_budget) * 100 if budget.montant_budget > 0 else 0.0
    
    return {
        "categorie": categorie,
        "periode": f"{mois:02d}/{annee}",
        "montant_total_depense": round(total_depense, 2),
        "budget_fixe": round(budget.montant_budget, 2),
        "montant_restant": round(montant_restant, 2),
        "pourcentage_consomme": round(pourcentage, 2)
    }


def verifier_depassement_budget(
    db: Session,
    categorie: str,
    mois: int,
    annee: int,
    montant_ajoute: float
) -> dict:
    """
    Vérifie si l'ajout d'une dépense ferait dépasser le budget de la catégorie.
    
    Returns:
        dict avec depasse (bool), message_alerte (str), montant_restant_avant (float),
        budget_fixe (float), montant_total_apres (float)
    """
    budget = db.query(Budget).filter(
        Budget.categorie == categorie,
        Budget.mois == mois,
        Budget.annee == annee
    ).first()
    
    if not budget:
        return {
            "depasse": False,
            "message_alerte": None,
            "montant_restant_avant": None,
            "budget_fixe": None,
            "montant_total_apres": None
        }
    
    total_actuel = calculer_total_depense_par_categorie(db, categorie, mois, annee)
    montant_restant_avant = budget.montant_budget - total_actuel
    montant_total_apres = total_actuel + montant_ajoute
    depasse = montant_total_apres > budget.montant_budget
    
    message_alerte = None
    if depasse:
        depassement = round(montant_total_apres - budget.montant_budget, 2)
        message_alerte = (
            f"Dépassement du budget {categorie} ({mois:02d}/{annee}) ! "
            f"Budget: {budget.montant_budget} €, après cette dépense: {montant_total_apres} € "
            f"(dépassement: {depassement} €)."
        )
    
    return {
        "depasse": depasse,
        "message_alerte": message_alerte,
        "montant_restant_avant": round(montant_restant_avant, 2),
        "budget_fixe": round(budget.montant_budget, 2),
        "montant_total_apres": round(montant_total_apres, 2)
    }
