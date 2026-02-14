# -*- coding: utf-8 -*-
"""Steps pour modification et suppression de budgets."""
from behave import given, when, then

MOIS_NUM = {"janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
            "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12}

@given('un budget "{categorie}" {montant:g} € {mois} {annee}')
def step_un_budget(context, categorie, montant, mois, annee):
    r = context.client.post("/api/budgets", json={
        "categorie": categorie,
        "montant_budget": float(montant),
        "mois": MOIS_NUM[mois.lower()],
        "annee": int(annee)
    })
    assert r.status_code == 201, r.text
    context.budget_id = r.json()["id"]

@when('je modifie ce budget à {montant:g} €')
def step_modifier_budget(context, montant):
    context.response = context.client.put(f"/api/budgets/{context.budget_id}", json={
        "montant_budget": float(montant)
    })

@then('le budget est mis à jour')
def step_budget_mis_a_jour(context):
    assert context.response.status_code == 200, context.response.text

@then('le montant du budget affiché est {montant:g} €')
def step_montant_budget_affiche(context, montant):
    assert context.response.json()["montant_budget"] == float(montant)

@when('je supprime ce budget')
def step_supprimer_budget(context):
    context.response = context.client.delete(f"/api/budgets/{context.budget_id}")

@then('le budget n\'existe plus')
def step_budget_nexiste_plus(context):
    assert context.response.status_code == 204
    r = context.client.get(f"/api/budgets/{context.budget_id}")
    assert r.status_code == 404

@then('la liste des budgets ne contient pas "{categorie}" pour {mois} {annee}')
def step_liste_sans_budget(context, categorie, mois, annee):
    r = context.client.get("/api/budgets")
    assert r.status_code == 200
    mois_n = MOIS_NUM[mois.lower()]
    for b in r.json():
        if b["categorie"] == categorie and b["mois"] == mois_n and b["annee"] == int(annee):
            raise AssertionError(f"Budget {categorie} {mois} {annee} trouvé alors qu'il aurait dû être supprimé")
