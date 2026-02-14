# language: fr
Fonctionnalité: Modification et suppression d'un budget
  En tant qu'utilisateur, je souhaite modifier le montant d'un budget existant
  ou supprimer un budget qui n'est plus pertinent.

  Contexte:
    Etant donné l'application est démarrée avec une base vide

  Scénario: Modifier le montant d'un budget
    Etant donné un budget "alimentation" 300 € janvier 2026
    Quand je modifie ce budget à 350 €
    Alors le budget est mis à jour
    Et le montant du budget affiché est 350 €

  Scénario: Supprimer un budget
    Etant donné un budget "loisirs" 100 € janvier 2026
    Quand je supprime ce budget
    Alors le budget n'existe plus
    Et la liste des budgets ne contient pas "loisirs" pour janvier 2026
