# -*- coding: utf-8 -*-
"""Steps pour l'export CSV."""
from behave import given, when, then

@given('une transaction "{libelle}" {montant:g} € {type_transaction} {categorie} {date_transaction}')
def step_une_transaction(context, libelle, montant, type_transaction, categorie, date_transaction):
    type_val = "depense" if type_transaction == "dépense" else "revenu"
    r = context.client.post("/api/transactions", json={
        "montant": float(montant),
        "libelle": libelle,
        "type": type_val,
        "categorie": categorie,
        "date_transaction": date_transaction
    })
    assert r.status_code == 201, r.text

@when('je demande l\'export CSV des transactions')
def step_export_csv(context):
    context.response = context.client.get("/api/transactions/export/csv")

@then('je reçois un fichier CSV')
def step_fichier_csv(context):
    assert context.response.status_code == 200
    assert "text/csv" in context.response.headers.get("content-type", "")

@then('le CSV contient les en-têtes id, date, libelle, type, categorie, montant')
def step_csv_headers(context):
    assert "id,date,libelle,type,categorie,montant" in context.response.text

@then('le CSV contient "{text1}" et "{text2}"')
def step_csv_contains(context, text1, text2):
    assert text1 in context.response.text
    assert text2 in context.response.text
