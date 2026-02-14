# language: fr
Fonctionnalité: Export des transactions en CSV
  En tant qu'utilisateur, je souhaite exporter mes transactions en fichier CSV
  pour les analyser ou les archiver en dehors de l'application.

  Contexte:
    Etant donné l'application est démarrée avec une base vide

  Scénario: Export CSV avec des transactions
    Etant donné une transaction "Courses" 25.50 € dépense alimentation 2026-01-06
    Et une transaction "Loyer" 800 € dépense logement 2026-01-01
    Quand je demande l'export CSV des transactions
    Alors je reçois un fichier CSV
    Et le CSV contient les en-têtes id, date, libelle, type, categorie, montant
    Et le CSV contient "Courses" et "25.5"
    Et le CSV contient "Loyer" et "800"
