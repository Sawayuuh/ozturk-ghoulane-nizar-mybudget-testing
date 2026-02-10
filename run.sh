#!/bin/bash
# Script de lancement de l'application

echo "🚀 Démarrage de l'application de gestion de budget..."

# Vérifier si le port 8000 est déjà utilisé
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Le port 8000 est déjà utilisé. Arrêt des processus existants..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    if ! python3 -m venv venv 2>/dev/null; then
        echo "❌ Erreur: python3-venv n'est pas installé."
        echo "   Installez-le avec: sudo apt install python3.10-venv"
        echo "   Ou utilisez directement: uvicorn app.main:app --reload"
        exit 1
    fi
fi

# Activer l'environnement virtuel si disponible
if [ -f "venv/bin/activate" ]; then
    echo "🔧 Activation de l'environnement virtuel..."
    source venv/bin/activate
    PIP_CMD="pip"
else
    echo "⚠️  Environnement virtuel non disponible, utilisation de pip système"
    PIP_CMD="pip3"
fi

# Installer les dépendances si nécessaire
if [ ! -f "venv/.installed" ] && [ -d "venv" ]; then
    echo "📥 Installation des dépendances..."
    $PIP_CMD install -r requirements.txt
    touch venv/.installed 2>/dev/null || true
elif [ ! -d "venv" ]; then
    echo "📥 Installation des dépendances (système)..."
    $PIP_CMD install -r requirements.txt --user
fi

# Démarrer le serveur
echo "🌟 Lancement du serveur sur http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
