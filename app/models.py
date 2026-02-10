from sqlalchemy import Column, Integer, String, Float, Date
from datetime import date
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    montant = Column(Float, nullable=False)
    libelle = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "revenu" ou "depense"
    categorie = Column(String, nullable=False)
    date_transaction = Column(Date, nullable=False, default=date.today)

    def __repr__(self):
        return f"<Transaction(id={self.id}, montant={self.montant}, libelle='{self.libelle}', type='{self.type}', categorie='{self.categorie}', date={self.date_transaction})>"


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    categorie = Column(String, nullable=False)
    montant_budget = Column(Float, nullable=False)
    mois = Column(Integer, nullable=False)  # 1-12
    annee = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Budget(id={self.id}, categorie='{self.categorie}', montant={self.montant_budget}, periode={self.mois}/{self.annee})>"
