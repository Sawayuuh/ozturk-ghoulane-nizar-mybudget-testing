"""Configuration Behave : base de test et client API."""
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from app.models import Transaction, Budget


def before_scenario(context, scenario):
    """Avant chaque scénario : recréer la base et un client de test."""
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    context.client = TestClient(app)
    context.transaction_ids = []
    context.budget_ids = []


def after_scenario(context, scenario):
    """Après chaque scénario : nettoyer."""
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
