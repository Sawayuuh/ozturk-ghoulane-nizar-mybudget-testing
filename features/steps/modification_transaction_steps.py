# -*- coding: utf-8 -*-
"""Steps pour la modification d'une transaction."""
from behave import given, when, then

@given('une transaction existante "{libelle}" {montant:g} € {type_transaction} {categorie} {date_transaction}')
def step_transaction_existante(context, libelle, montant, type_transaction, categorie, date_transaction):
    type_val = "depense" if type_transaction == "dépense" else "revenu"
    r = context.client.post("/api/transactions", json={
        "montant": float(montant),
        "libelle": libelle,
        "type": type_val,
        "categorie": categorie,
        "date_transaction": date_transaction
    })
    assert r.status_code == 201, r.text
    context.transaction_id = r.json()["id"]

@when('je modifie cette transaction en "{libelle}" {montant:g} €')
def step_modifier_transaction(context, libelle, montant):
    r = context.client.get(f"/api/transactions/{context.transaction_id}")
    data = r.json()
    context.response = context.client.put(f"/api/transactions/{context.transaction_id}", json={
        "montant": float(montant),
        "libelle": libelle,
        "type": data["type"],
        "categorie": data["categorie"],
        "date_transaction": data["date_transaction"]
    })

@then('la transaction est mise à jour')
def step_transaction_mise_a_jour(context):
    assert context.response.status_code == 200, context.response.text

@then('le montant affiché est {montant:g} €')
def step_montant_affiche(context, montant):
    assert context.response.json()["montant"] == float(montant)

@then('le libellé affiché est "{libelle}"')
def step_libelle_affiche(context, libelle):
    assert context.response.json()["libelle"] == libelle
