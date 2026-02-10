from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional


class TransactionBase(BaseModel):
    montant: float = Field(..., gt=0, description="Montant de la transaction (doit être positif)")
    libelle: str = Field(..., min_length=1, description="Description de la transaction")
    type: str = Field(..., description="Type: 'revenu' ou 'depense'")
    categorie: str = Field(..., min_length=1, description="Catégorie de la transaction")
    date_transaction: date = Field(default_factory=date.today, description="Date de la transaction")

    @validator('type')
    def validate_type(cls, v):
        if v not in ['revenu', 'depense']:
            raise ValueError("Le type doit être 'revenu' ou 'depense'")
        return v

    @validator('montant')
    def validate_montant(cls, v):
        if v <= 0:
            raise ValueError("Le montant doit être strictement positif")
        return v


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int

    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    categorie: str = Field(..., min_length=1, description="Catégorie du budget")
    montant_budget: float = Field(..., gt=0, description="Montant du budget (doit être positif)")
    mois: int = Field(..., ge=1, le=12, description="Mois (1-12)")
    annee: int = Field(..., ge=2000, le=2100, description="Année")

    @validator('montant_budget')
    def validate_montant(cls, v):
        if v <= 0:
            raise ValueError("Le montant du budget doit être strictement positif")
        return v


class BudgetCreate(BudgetBase):
    pass


class BudgetResponse(BudgetBase):
    id: int

    class Config:
        from_attributes = True


class BudgetStatResponse(BaseModel):
    categorie: str
    periode: str  # "01/2026"
    montant_total_depense: float
    budget_fixe: float
    montant_restant: float
    pourcentage_consomme: float

    class Config:
        from_attributes = True
