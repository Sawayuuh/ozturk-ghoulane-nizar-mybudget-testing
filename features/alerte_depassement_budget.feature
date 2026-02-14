# language: fr
Fonctionnalité: Alerte de dépassement de budget
  En tant qu'utilisateur, je souhaite être alerté quand une dépense fait dépasser
  mon budget de catégorie, afin de mieux contrôler mes finances.

  Contexte:
    Etant donné l'application est démarrée avec une base vide

  Scénario: Dépassement du budget alimentation
    Etant donné un budget "alimentation" de 300 € pour janvier 2026
    Et des dépenses existantes "alimentation" de 290 € en janvier 2026
    Quand j'ajoute une dépense "alimentation" de 20 € en janvier 2026
    Alors la transaction est enregistrée
    Et je reçois une alerte de dépassement de budget
    Et le message d'alerte indique le dépassement

  Scénario: Pas d'alerte quand on reste sous le budget
    Etant donné un budget "alimentation" de 300 € pour janvier 2026
    Et des dépenses existantes "alimentation" de 100 € en janvier 2026
    Quand j'ajoute une dépense "alimentation" de 50 € en janvier 2026
    Alors la transaction est enregistrée
    Et je ne reçois pas d'alerte de dépassement
