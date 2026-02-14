from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import io
import csv

from app.database import get_db, init_db
from app.models import Transaction, Budget
from app.schemas import (
    TransactionCreate, TransactionResponse, TransactionCreateResponse,
    BudgetCreate, BudgetResponse, BudgetStatResponse, BudgetUpdate
)
from app import business_logic

app = FastAPI(title="Gestion de Budget Personnel", version="1.0.0")

# Initialiser la base de données au démarrage
@app.on_event("startup")
def startup_event():
    init_db()

# Servir les fichiers statiques (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    """Redirige vers l'interface web"""
    return FileResponse("static/index.html")


# ========== ENDPOINTS TRANSACTIONS ==========

@app.post("/api/transactions", response_model=TransactionCreateResponse, status_code=201)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle transaction. Retourne une alerte si la dépense dépasse le budget."""
    alerte = None
    if transaction.type == "depense":
        alerte = business_logic.verifier_depassement_budget(
            db, transaction.categorie,
            transaction.date_transaction.month, transaction.date_transaction.year,
            transaction.montant
        )
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    result = TransactionCreateResponse.model_validate(db_transaction)
    if alerte and alerte["depasse"]:
        result.alerte_depassement = True
        result.message_alerte = alerte["message_alerte"]
    return result


@app.get("/api/transactions", response_model=List[TransactionResponse])
def list_transactions(
    categorie: Optional[str] = Query(None, description="Filtrer par catégorie"),
    date_debut: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    date_fin: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Liste toutes les transactions avec filtres optionnels"""
    query = db.query(Transaction)
    
    if categorie:
        query = query.filter(Transaction.categorie == categorie)
    
    if date_debut:
        query = query.filter(Transaction.date_transaction >= date_debut)
    
    if date_fin:
        query = query.filter(Transaction.date_transaction <= date_fin)
    
    transactions = query.order_by(Transaction.date_transaction.desc()).all()
    return transactions


@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Récupère une transaction par son ID"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    return transaction


@app.put("/api/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """Modifie une transaction existante"""
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    for key, value in transaction.model_dump().items():
        setattr(db_transaction, key, value)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.delete("/api/transactions/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Supprime une transaction"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    db.delete(transaction)
    db.commit()
    return None


@app.get("/api/transactions/export/csv")
def export_transactions_csv(
    categorie: Optional[str] = Query(None),
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Exporte les transactions en CSV."""
    query = db.query(Transaction)
    if categorie:
        query = query.filter(Transaction.categorie == categorie)
    if date_debut:
        query = query.filter(Transaction.date_transaction >= date_debut)
    if date_fin:
        query = query.filter(Transaction.date_transaction <= date_fin)
    transactions = query.order_by(Transaction.date_transaction.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "date", "libelle", "type", "categorie", "montant"])
    for t in transactions:
        writer.writerow([
            t.id, t.date_transaction.isoformat(), t.libelle, t.type, t.categorie, t.montant
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"}
    )


# ========== ENDPOINTS BUDGETS ==========

@app.post("/api/budgets", response_model=BudgetResponse, status_code=201)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    """Crée un nouveau budget pour une catégorie et une période"""
    # Vérifier si un budget existe déjà pour cette catégorie et période
    existing = db.query(Budget).filter(
        Budget.categorie == budget.categorie,
        Budget.mois == budget.mois,
        Budget.annee == budget.annee
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Un budget existe déjà pour la catégorie '{budget.categorie}' en {budget.mois:02d}/{budget.annee}"
        )
    
    db_budget = Budget(**budget.model_dump())
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@app.get("/api/budgets", response_model=List[BudgetResponse])
def list_budgets(
    categorie: Optional[str] = Query(None, description="Filtrer par catégorie"),
    mois: Optional[int] = Query(None, ge=1, le=12, description="Filtrer par mois"),
    annee: Optional[int] = Query(None, description="Filtrer par année"),
    db: Session = Depends(get_db)
):
    """Liste tous les budgets avec filtres optionnels"""
    query = db.query(Budget)
    
    if categorie:
        query = query.filter(Budget.categorie == categorie)
    
    if mois:
        query = query.filter(Budget.mois == mois)
    
    if annee:
        query = query.filter(Budget.annee == annee)
    
    budgets = query.order_by(Budget.annee.desc(), Budget.mois.desc()).all()
    return budgets


@app.get("/api/budgets/stats/{categorie}", response_model=BudgetStatResponse)
def get_budget_stats(
    categorie: str,
    mois: int = Query(..., ge=1, le=12, description="Mois (1-12)"),
    annee: int = Query(..., ge=2000, description="Année"),
    db: Session = Depends(get_db)
):
    """Obtient les statistiques d'un budget pour une catégorie et une période"""
    stats = business_logic.obtenir_statistiques_budget(db, categorie, mois, annee)
    return BudgetStatResponse(**stats)


@app.get("/api/budgets/stats", response_model=List[BudgetStatResponse])
def list_all_budget_stats(
    mois: Optional[int] = Query(None, ge=1, le=12, description="Mois (1-12)"),
    annee: Optional[int] = Query(None, ge=2000, description="Année"),
    db: Session = Depends(get_db)
):
    """Liste les statistiques de tous les budgets pour une période donnée"""
    if not mois or not annee:
        raise HTTPException(
            status_code=400,
            detail="Les paramètres 'mois' et 'annee' sont requis"
        )
    
    budgets = db.query(Budget).filter(
        Budget.mois == mois,
        Budget.annee == annee
    ).all()
    
    stats_list = []
    for budget in budgets:
        stats = business_logic.obtenir_statistiques_budget(
            db, budget.categorie, budget.mois, budget.annee
        )
        stats_list.append(BudgetStatResponse(**stats))
    
    return stats_list


@app.get("/api/budgets/{budget_id}", response_model=BudgetResponse)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    """Récupère un budget par son ID"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget non trouvé")
    return budget


@app.put("/api/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    db: Session = Depends(get_db)
):
    """Modifie un budget existant"""
    db_budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget non trouvé")
    data = budget_update.model_dump(exclude_unset=True)
    if data:
        for key, value in data.items():
            setattr(db_budget, key, value)
        existing = db.query(Budget).filter(
            Budget.categorie == db_budget.categorie,
            Budget.mois == db_budget.mois,
            Budget.annee == db_budget.annee,
            Budget.id != budget_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Un budget existe déjà pour la catégorie '{db_budget.categorie}' en {db_budget.mois:02d}/{db_budget.annee}"
            )
    db.commit()
    db.refresh(db_budget)
    return db_budget


@app.delete("/api/budgets/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    """Supprime un budget"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget non trouvé")
    db.delete(budget)
    db.commit()
    return None
