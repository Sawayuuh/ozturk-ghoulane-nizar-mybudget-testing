const API_BASE = '/api';

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    // Définir la date du jour par défaut
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date_transaction').value = today;
    
    // Définir le mois et l'année actuels
    const now = new Date();
    document.getElementById('budget-mois').value = now.getMonth() + 1;
    document.getElementById('budget-annee').value = now.getFullYear();
    document.getElementById('stats-mois').value = now.getMonth() + 1;
    document.getElementById('stats-annee').value = now.getFullYear();
    
    // Charger les données initiales
    loadTransactions();
    loadBudgets();
    loadStats();
    
    // Écouteurs d'événements
    document.getElementById('transaction-form').addEventListener('submit', handleTransactionSubmit);
    document.getElementById('budget-form').addEventListener('submit', handleBudgetSubmit);
});

// Gestion des onglets
function showTab(tabName) {
    // Masquer tous les onglets
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Afficher l'onglet sélectionné
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Transactions (édition en cours)
let editingTransactionId = null;

async function handleTransactionSubmit(e) {
    e.preventDefault();
    
    const transaction = {
        montant: parseFloat(document.getElementById('montant').value),
        libelle: document.getElementById('libelle').value,
        type: document.getElementById('type').value,
        categorie: document.getElementById('categorie').value,
        date_transaction: document.getElementById('date_transaction').value
    };
    
    try {
        const url = editingTransactionId
            ? `${API_BASE}/transactions/${editingTransactionId}`
            : `${API_BASE}/transactions`;
        const method = editingTransactionId ? 'PUT' : 'POST';
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(transaction)
        });
        
        if (response.ok) {
            const data = await response.json();
            const wasEditing = !!editingTransactionId;
            document.getElementById('transaction-form').reset();
            document.getElementById('date_transaction').value = new Date().toISOString().split('T')[0];
            editingTransactionId = null;
            const btn = document.getElementById('transaction-submit-btn');
            if (btn) btn.textContent = 'Ajouter';
            loadTransactions();
            if (wasEditing) {
                alert('Transaction modifiée avec succès !');
            } else if (data.alerte_depassement && data.message_alerte) {
                alert('⚠️ Alerte dépassement de budget\n\n' + data.message_alerte);
            } else {
                alert('Transaction ajoutée avec succès !');
            }
        } else {
            const error = await response.json();
            alert(`Erreur: ${error.detail || 'Erreur lors de l\'enregistrement'}`);
        }
    } catch (error) {
        alert(`Erreur: ${error.message}`);
    }
}

async function editTransaction(id) {
    try {
        const response = await fetch(`${API_BASE}/transactions/${id}`);
        if (!response.ok) return;
        const t = await response.json();
        document.getElementById('montant').value = t.montant;
        document.getElementById('libelle').value = t.libelle;
        document.getElementById('type').value = t.type;
        document.getElementById('categorie').value = t.categorie;
        document.getElementById('date_transaction').value = t.date_transaction;
        editingTransactionId = id;
        const btn = document.getElementById('transaction-submit-btn');
        if (btn) btn.textContent = 'Enregistrer la modification';
    } catch (err) {
        alert('Erreur: ' + err.message);
    }
}

async function loadTransactions() {
    const categorie = document.getElementById('filter-categorie').value;
    const dateDebut = document.getElementById('filter-date-debut').value;
    const dateFin = document.getElementById('filter-date-fin').value;
    
    let url = `${API_BASE}/transactions?`;
    const params = [];
    if (categorie) params.push(`categorie=${encodeURIComponent(categorie)}`);
    if (dateDebut) params.push(`date_debut=${dateDebut}`);
    if (dateFin) params.push(`date_fin=${dateFin}`);
    url += params.join('&');
    
    try {
        const response = await fetch(url);
        const transactions = await response.json();
        displayTransactions(transactions);
    } catch (error) {
        console.error('Erreur lors du chargement des transactions:', error);
    }
}

function displayTransactions(transactions) {
    const container = document.getElementById('transactions-list');
    
    if (transactions.length === 0) {
        container.innerHTML = '<div class="empty-message">Aucune transaction trouvée</div>';
        return;
    }
    
    const table = `
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Libellé</th>
                    <th>Type</th>
                    <th>Catégorie</th>
                    <th>Montant</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${transactions.map(t => `
                    <tr>
                        <td>${new Date(t.date_transaction).toLocaleDateString('fr-FR')}</td>
                        <td>${t.libelle}</td>
                        <td><span class="badge badge-${t.type}">${t.type}</span></td>
                        <td>${t.categorie}</td>
                        <td>${t.montant.toFixed(2)} €</td>
                        <td>
                            <button class="btn btn-secondary" onclick="editTransaction(${t.id})">Modifier</button>
                            <button class="btn btn-danger" onclick="deleteTransaction(${t.id})">Supprimer</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    container.innerHTML = table;
}

async function deleteTransaction(id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette transaction ?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/transactions/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadTransactions();
            alert('Transaction supprimée avec succès !');
        }
    } catch (error) {
        alert(`Erreur: ${error.message}`);
    }
}

function clearFilters() {
    document.getElementById('filter-categorie').value = '';
    document.getElementById('filter-date-debut').value = '';
    document.getElementById('filter-date-fin').value = '';
    loadTransactions();
}

function exportTransactionsCsv() {
    const categorie = document.getElementById('filter-categorie').value;
    const dateDebut = document.getElementById('filter-date-debut').value;
    const dateFin = document.getElementById('filter-date-fin').value;
    let url = `${API_BASE}/transactions/export/csv?`;
    const params = [];
    if (categorie) params.push(`categorie=${encodeURIComponent(categorie)}`);
    if (dateDebut) params.push(`date_debut=${dateDebut}`);
    if (dateFin) params.push(`date_fin=${dateFin}`);
    url += params.join('&');
    window.location.href = url;
}

// Budgets
async function handleBudgetSubmit(e) {
    e.preventDefault();
    
    const budget = {
        categorie: document.getElementById('budget-categorie').value,
        montant_budget: parseFloat(document.getElementById('budget-montant').value),
        mois: parseInt(document.getElementById('budget-mois').value),
        annee: parseInt(document.getElementById('budget-annee').value)
    };
    
    try {
        const response = await fetch(`${API_BASE}/budgets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(budget)
        });
        
        if (response.ok) {
            document.getElementById('budget-form').reset();
            const now = new Date();
            document.getElementById('budget-mois').value = now.getMonth() + 1;
            document.getElementById('budget-annee').value = now.getFullYear();
            loadBudgets();
            loadStats();
            alert('Budget créé avec succès !');
        } else {
            const error = await response.json();
            alert(`Erreur: ${error.detail || 'Erreur lors de la création'}`);
        }
    } catch (error) {
        alert(`Erreur: ${error.message}`);
    }
}

async function loadBudgets() {
    try {
        const response = await fetch(`${API_BASE}/budgets`);
        const budgets = await response.json();
        displayBudgets(budgets);
    } catch (error) {
        console.error('Erreur lors du chargement des budgets:', error);
    }
}

function displayBudgets(budgets) {
    const container = document.getElementById('budgets-list');
    
    if (budgets.length === 0) {
        container.innerHTML = '<div class="empty-message">Aucun budget défini</div>';
        return;
    }
    
    const table = `
        <table>
            <thead>
                <tr>
                    <th>Catégorie</th>
                    <th>Mois</th>
                    <th>Année</th>
                    <th>Montant</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${budgets.map(b => `
                    <tr>
                        <td>${b.categorie}</td>
                        <td>${getMonthName(b.mois)}</td>
                        <td>${b.annee}</td>
                        <td>${b.montant_budget.toFixed(2)} €</td>
                        <td>
                            <button class="btn btn-secondary" onclick="editBudget(${b.id})">Modifier</button>
                            <button class="btn btn-danger" onclick="deleteBudget(${b.id})">Supprimer</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    container.innerHTML = table;
}

async function editBudget(id) {
    const montant = prompt('Nouveau montant du budget (€) :');
    if (montant === null) return;
    const value = parseFloat(montant);
    if (isNaN(value) || value <= 0) {
        alert('Montant invalide.');
        return;
    }
    try {
        const response = await fetch(`${API_BASE}/budgets/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ montant_budget: value })
        });
        if (response.ok) {
            loadBudgets();
            loadStats();
            alert('Budget modifié.');
        } else {
            const err = await response.json();
            alert('Erreur: ' + (err.detail || 'Erreur'));
        }
    } catch (e) {
        alert('Erreur: ' + e.message);
    }
}

async function deleteBudget(id) {
    if (!confirm('Supprimer ce budget ?')) return;
    try {
        const response = await fetch(`${API_BASE}/budgets/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadBudgets();
            loadStats();
            alert('Budget supprimé.');
        } else {
            alert('Erreur lors de la suppression.');
        }
    } catch (e) {
        alert('Erreur: ' + e.message);
    }
}

// Statistiques
async function loadStats() {
    const mois = document.getElementById('stats-mois').value;
    const annee = document.getElementById('stats-annee').value;
    
    if (!mois || !annee) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/budgets/stats?mois=${mois}&annee=${annee}`);
        const stats = await response.json();
        displayStats(stats);
    } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
    }
}

function displayStats(stats) {
    const container = document.getElementById('stats-list');
    
    if (stats.length === 0) {
        container.innerHTML = '<div class="empty-message">Aucune statistique disponible pour cette période</div>';
        return;
    }
    
    const cards = stats.map(stat => {
        const pourcentage = Math.min(stat.pourcentage_consomme, 100);
        const progressClass = stat.pourcentage_consomme > 100 ? 'danger' : 
                             stat.pourcentage_consomme > 80 ? 'warning' : '';
        
        return `
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-title">${stat.categorie}</span>
                    <span class="stat-value ${stat.montant_restant >= 0 ? 'positive' : 'negative'}">
                        ${stat.montant_restant >= 0 ? '+' : ''}${stat.montant_restant.toFixed(2)} €
                    </span>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Dépensé: ${stat.montant_total_depense.toFixed(2)} €</span>
                        <span>Budget: ${stat.budget_fixe.toFixed(2)} €</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill ${progressClass}" style="width: ${pourcentage}%"></div>
                    </div>
                    <div style="text-align: center; margin-top: 5px; font-weight: bold;">
                        ${stat.pourcentage_consomme.toFixed(1)}% consommé
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = cards;
}

// Utilitaires
function getMonthName(month) {
    const months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                   'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
    return months[month - 1];
}



