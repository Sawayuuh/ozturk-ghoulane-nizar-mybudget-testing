# language: fr
Fonctionnalité: Modification d'une transaction
  En tant qu'utilisateur, je souhaite corriger une transaction déjà saisie
  (montant, libellé, date, etc.) sans la supprimer.

  Contexte:
    Etant donné l'application est démarrée avec une base vide

  Scénario: Modifier le montant et le libellé d'une transaction
    Etant donné une transaction existante "Courses" 25.50 € dépense alimentation 2026-01-06
    Quand je modifie cette transaction en "Courses Leclerc" 30.00 €
    Alors la transaction est mise à jour
    Et le montant affiché est 30.00 €
    Et le libellé affiché est "Courses Leclerc"
