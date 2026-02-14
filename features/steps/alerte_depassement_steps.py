# -*- coding: utf-8 -*-
"""Steps pour l'alerte de dépassement de budget."""
from behave import given, when, then

@given('un budget "{categorie}" de {montant:g} € pour {mois} {annee}')
def step_budget(context, categorie, montant, mois, annee):
    mois_num = {"janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
                "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12}[mois.lower()]
    r = context.client.post("/api/budgets", json={
        "categorie": categorie,
        "montant_budget": float(montant),
        "mois": mois_num,
        "annee": int(annee)
    })
    assert r.status_code == 201, r.text
    context.budget_ids.append(r.json()["id"])

@given('des dépenses existantes "{categorie}" de {total:g} € en {mois} {annee}')
def step_depenses_existantes(context, categorie, total, mois, annee):
    mois_num = {"janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
                "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12}[mois.lower()]
    # Une seule dépense du montant total pour simplifier
    r = context.client.post("/api/transactions", json={
        "montant": float(total),
        "libelle": "Dépense existante",
        "type": "depense",
        "categorie": categorie,
        "date_transaction": f"{int(annee)}-{mois_num:02d}-15"
    })
    assert r.status_code == 201, r.text

@when('j\'ajoute une dépense "{categorie}" de {montant:g} € en {mois} {annee}')
def step_ajoute_depense(context, categorie, montant, mois, annee):
    mois_num = {"janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
                "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12}[mois.lower()]
    context.response = context.client.post("/api/transactions", json={
        "montant": float(montant),
        "libelle": "Nouvelle dépense",
        "type": "depense",
        "categorie": categorie,
        "date_transaction": f"{int(annee)}-{mois_num:02d}-20"
    })

@then('la transaction est enregistrée')
def step_transaction_enregistree(context):
    assert context.response.status_code == 201, context.response.text

@then('je reçois une alerte de dépassement de budget')
def step_alerte_recue(context):
    data = context.response.json()
    assert data.get("alerte_depassement") is True, data

@then('le message d\'alerte indique le dépassement')
def step_message_alerte(context):
    data = context.response.json()
    assert data.get("message_alerte"), "Pas de message d'alerte"
    assert "Dépassement" in data["message_alerte"] or "dépassement" in data["message_alerte"].lower()

@then('je ne reçois pas d\'alerte de dépassement')
def step_pas_alerte(context):
    data = context.response.json()
    assert not data.get("alerte_depassement"), data.get("message_alerte", "")
