import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

from app.database import Base, get_db
from app.models import Transaction, Budget


# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Crée une nouvelle base de données pour chaque test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_transactions(db_session):
    """Crée des transactions de test"""
    transactions = [
        Transaction(
            montant=25.50,
            libelle="Courses Leclerc",
            type="depense",
            categorie="alimentation",
            date_transaction=date(2026, 1, 6)
        ),
        Transaction(
            montant=800.0,
            libelle="Loyer janvier",
            type="depense",
            categorie="logement",
            date_transaction=date(2026, 1, 1)
        ),
        Transaction(
            montant=50.0,
            libelle="Restaurant",
            type="depense",
            categorie="alimentation",
            date_transaction=date(2026, 1, 15)
        ),
        Transaction(
            montant=2000.0,
            libelle="Salaire",
            type="revenu",
            categorie="salaire",
            date_transaction=date(2026, 1, 1)
        ),
    ]
    for t in transactions:
        db_session.add(t)
    db_session.commit()
    return transactions


@pytest.fixture
def sample_budgets(db_session):
    """Crée des budgets de test"""
    budgets = [
        Budget(
            categorie="alimentation",
            montant_budget=300.0,
            mois=1,
            annee=2026
        ),
        Budget(
            categorie="logement",
            montant_budget=800.0,
            mois=1,
            annee=2026
        ),
    ]
    for b in budgets:
        db_session.add(b)
    db_session.commit()
    return budgets
